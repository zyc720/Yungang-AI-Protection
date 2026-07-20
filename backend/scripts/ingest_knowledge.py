"""
Knowledge base ingestion: parse the dictionary MD, build chunks, and insert into Milvus.

Usage:
    cd backend
    python scripts/ingest_knowledge.py [--dry-run] [--json-output chunks.json]

The script:
1. Parses the MD file body to extract ~2,320 dictionary entries
2. Splits entries into categories (15 major categories)
3. Applies chunking strategy:
   - Short entries (<200 chars) → merge 2-5 adjacent entries in same category
   - Medium entries (200-1000 chars) → 1 entry = 1 chunk
   - Long entries (>1000 chars) → split by paragraph boundaries
4. Associates images with their containing entries
5. Inserts chunks into Milvus with BGE-M3 embeddings
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MD_FILE = PROJECT_ROOT / "outputs/云冈石窟辞典/auto/云冈石窟辞典.md"
CONTENT_LIST_FILE = PROJECT_ROOT / "outputs/云冈石窟辞典/auto/云冈石窟辞典_content_list.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "backend" / "data" / "chunks.json"

# The 15 major categories in body order
CATEGORIES = [
    "寺院洞窟",
    "历 史",
    "佛 教",
    "窟龛形制",
    "佛教造像",
    "佛经故事",
    "装饰图案",
    "音乐舞蹈",
    "石窟附属",
    "石窟关联",
    "碑文铭记",
    "保护管理",
    "考古文论",
    "历史人物",
    "考察访问·词赋",
]

# Category aliases: body heading text -> canonical category name
CATEGORY_ALIASES = {
    "历 史": "历 史",
    "访问·辞赋": "考察访问·词赋",
    "访问·词赋": "考察访问·词赋",
}

# Sections to skip (not real dictionary entries)
SKIP_TITLES = {
    "凡 例", "主要资料来源", "目 录", "正文分类目录",
    "正文插图目录", "词目笔画索引", "汉语拼音索引",
    "云冈石窟编号洞窟现存佛教造像数量统计表",
    "云冈石窟历史大事年记",
}

# Chunking thresholds
SHORT_THRESHOLD = 200      # chars: merge with adjacent entries
LONG_THRESHOLD = 3000       # chars: split into sub-chunks (only 113 entries > 3000)
MAX_MERGE_COUNT = 5         # max entries per merged chunk
MAX_CHUNK_SIZE = 1500       # target max chars per chunk when splitting
MIN_SPLIT_SIZE = 300        # min chars per sub-chunk (merge smaller ones)

# Pattern: lines starting with # or ## (Markdown headers)
HEADER_PATTERN = re.compile(r'^#{1,2}\s')
IMG_PATTERN = re.compile(r'!\[.*?\]\(images/(img_\d+\.jpg)\)')

# Cross-reference pattern (e.g., 见"第20窟"条)
# Uses Chinese fancy quotes (U+201C/U+201D) and 「」(U+300C/U+300D)
CROSS_REF_PATTERN = re.compile(r'见[“「](.+?)[”」]条')


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class Entry:
    """A single dictionary entry extracted from the MD body."""
    title: str               # e.g. "第1窟" (cleaned, no pinyin)
    title_with_pinyin: str   # e.g. "第1 窟(dì 1 kū)"
    content: str             # Full text content (may include image refs)
    category: str            # Which of the 15 categories
    page: int | None = None  # Page number (if extractable)
    image_ids: list[str] = field(default_factory=list)  # Associated images
    cross_refs: list[str] = field(default_factory=list)  # Cross-referenced entries
    line_number: int = 0     # Source line in MD


@dataclass
class Chunk:
    """A knowledge chunk ready for Milvus ingestion."""
    entry_id: str            # Primary entry identifier
    title: str               # For citation matching
    category: str            # Parent category
    chunk_id: str            # Unique chunk ID
    content: str             # Text content
    chunk_index: int = 0     # Sub-chunk index (0 for standalone/merged)
    image_ids: list[str] = field(default_factory=list)
    cross_refs: list[str] = field(default_factory=list)
    merged_entries: list[str] = field(default_factory=list)
    is_merged: bool = False


# ============================================================================
# Step 1: Parse MD Body
# ============================================================================

def parse_entries(md_path: Path) -> list[Entry]:
    """Parse the MD file and extract all dictionary entries from the body.

    Skips front matter (序, TOC) and back matter (indices).
    Groups entries by their parent category.
    """
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")

    # Find the first real body category header (after TOC and illustration index)
    body_start = _find_body_start(lines)
    logger.info("Body starts at line %d", body_start + 1)

    # Build category boundary map
    cat_map = _build_category_map(lines, body_start)
    logger.info("Found %d categories in body", len(cat_map))

    # Extract entries
    entries = _extract_entries(lines, body_start, cat_map)
    logger.info("Extracted %d entries", len(entries))

    # Post-process: extract cross-refs from stripped content
    for entry in entries:
        entry.cross_refs = CROSS_REF_PATTERN.findall(entry.content)

    return entries


def _find_body_start(lines: list[str]) -> int:
    """Find the first category header that starts the actual body content."""
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "## 寺院洞窟" and i > 2500:
            return i
    raise ValueError("Cannot find body start (## 寺院洞窟 after line 2500)")


def _build_category_map(lines: list[str], body_start: int) -> list[tuple[int, str]]:
    """Build ordered list of (line_number, category_name) boundaries.

    Handles both H2 (## 寺院洞窟) and H1 (# 历 史) category headers.
    """
    boundaries = []
    for i in range(body_start, len(lines)):
        stripped = lines[i].strip()

        # H2 category headers
        if stripped.startswith("## "):
            title = stripped[3:].strip()
            if title in CATEGORIES:
                boundaries.append((i, title))
            elif title in CATEGORY_ALIASES:
                boundaries.append((i, CATEGORY_ALIASES[title]))

        # H1 category headers (e.g. # 历 史)
        elif stripped.startswith("# ") and not stripped.startswith("## "):
            title = stripped[2:].strip()
            if title in CATEGORIES:
                boundaries.append((i, title))
            elif title in CATEGORY_ALIASES:
                boundaries.append((i, CATEGORY_ALIASES[title]))

    return boundaries


def _extract_entries(
    lines: list[str], body_start: int, cat_map: list[tuple[int, str]]
) -> list[Entry]:
    """Extract all entries between category boundaries.

    Uses a simple scan through all lines: each H2 or H1 header (with pinyin)
    that isn't a category marker or skip-title is treated as an entry.
    The current_category is tracked via the category map.
    """
    entries = []
    current_category = "未知"

    # Build quick lookup: line_number -> category name
    cat_line_to_name = {line_no: name for line_no, name in cat_map}

    # Find index section start
    index_start = len(lines)
    for i in range(body_start, len(lines)):
        if lines[i].strip() == "## 词目笔画索引":
            index_start = i
            break

    # Scan each line
    for i in range(body_start, index_start):
        line = lines[i].strip()

        # Update current_category at boundaries
        if i in cat_line_to_name:
            current_category = cat_line_to_name[i]
            continue

        entry_header = None

        # Detect H2 entry headers (## 标题(pinyin))
        if line.startswith("## "):
            title_raw = line[3:].strip()
            if title_raw not in CATEGORIES and title_raw not in SKIP_TITLES:
                entry_header = title_raw

        # Detect H1 entry headers (# 标题(pinyin)) — only if they have pinyin
        elif line.startswith("# ") and not line.startswith("## "):
            title_raw = line[2:].strip()
            if (title_raw not in CATEGORIES and title_raw not in SKIP_TITLES
                    and re.match(r'.+\([a-zāáǎàōóǒòēéěèīíǐìūúǔùǖǘǚǜ].+\)', title_raw)):
                entry_header = title_raw

        if not entry_header:
            continue

        entry_title = _clean_title(entry_header)
        if not entry_title:
            continue

        # Gather content: all non-header lines until the next header
        content_lines = []
        for j in range(i + 1, index_start):
            next_line = lines[j].strip()
            if HEADER_PATTERN.match(next_line):
                break
            content_lines.append(lines[j])

        raw_content = "\n".join(content_lines).strip()

        # Extract image IDs before stripping
        image_ids = IMG_PATTERN.findall(raw_content)

        # Strip image markdown and captions — keep only plain text
        content = _strip_images_from_content(raw_content)

        if content and len(content) >= 5:
            entries.append(Entry(
                title=entry_title,
                title_with_pinyin=_clean_title_with_pinyin(entry_header),
                content=content,
                category=current_category,
                image_ids=image_ids,
                line_number=i + 1,
            ))

    return entries


def _clean_title(raw: str) -> str:
    """Clean entry title: remove pinyin, normalize spaces."""
    # Remove pinyin in parens: "第1 窟(dì 1 kū)" -> "第1窟"
    title = re.sub(r'\([^)]+\)', '', raw).strip()
    # Normalize spaces around digits: "第1 窟" -> "第1窟"
    title = re.sub(r'(\d)\s+', r'\1', title)
    # Clean other spaces
    title = re.sub(r'\s+', '', title) if title else title
    return title


def _clean_title_with_pinyin(raw: str) -> str:
    """Keep pinyin but normalize: '第1 窟(dì 1 kū)' -> '第1窟(dì 1 kū)'"""
    match = re.match(r'^(.+?)\((.+?)\)$', raw.strip())
    if match:
        body = re.sub(r'(\d)\s+', r'\1', match.group(1).strip())
        body = re.sub(r'\s+', '', body)
        return f"{body}({match.group(2).strip()})"
    body = re.sub(r'(\d)\s+', r'\1', raw.strip())
    body = re.sub(r'\s+', '', body)
    return body


def _strip_images_from_content(content: str) -> str:
    """Remove image markdown and standalone image caption lines from content.

    Image references like ![](images/img_042.jpg) are removed, as are
    single-line image captions that immediately follow an image on the
    next line (e.g. "第 20 窟露天大佛").
    """
    # Remove image markdown: ![](images/img_NNN.jpg)
    content = IMG_PATTERN.sub('', content)

    # Remove lines that are purely image captions (short lines after image removal
    # that look like standalone captions: "第 X 窟...")
    lines = content.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip empty lines
        if not stripped:
            cleaned.append(line)
            continue
        # Skip short caption-like lines (typically 5-30 chars, single sentence)
        # These are usually image captions like "第6窟东壁千佛龛"
        if len(stripped) < 40 and not stripped.endswith(('。', '！', '？', '；')):
            # Check if it looks like a caption (starts with "第" or is very short)
            if stripped.startswith('第') or len(stripped) < 15:
                continue
        cleaned.append(line)

    # Remove excessive blank lines (3+ → 2)
    text = '\n'.join(cleaned)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ============================================================================
# Step 2: Chunking
# ============================================================================

def build_chunks(entries: list[Entry]) -> list[Chunk]:
    """Apply chunking strategy to entries.

    Strategy:
    - Short (<200 chars, no images) → merge adjacent same-category
    - Medium (200-1000 chars) → 1:1
    - Long (>1000 chars) → split by paragraph
    """
    chunks: list[Chunk] = []
    merge_buffer: list[Entry] = []
    global_chunk_idx = 0
    merged_group_idx = 0

    def _flush_buffer() -> None:
        nonlocal global_chunk_idx, merged_group_idx
        if not merge_buffer:
            return

        if len(merge_buffer) == 1:
            # Single entry that was in buffer — treat as medium
            entry = merge_buffer[0]
            chunks.append(_entry_to_chunk(entry, global_chunk_idx))
            global_chunk_idx += 1
        else:
            # Merge multiple short entries
            merged_group_idx += 1
            chunk = _merge_entries(merge_buffer, merged_group_idx, global_chunk_idx)
            chunks.append(chunk)
            global_chunk_idx += 1
        merge_buffer.clear()

    prev_category = ""
    for entry in entries:
        # Flush buffer on category change
        if entry.category != prev_category and merge_buffer:
            _flush_buffer()
        prev_category = entry.category

        content_len = len(entry.content)
        has_image = bool(entry.image_ids)

        if content_len < SHORT_THRESHOLD and not has_image:
            # Short entry → buffer for merging
            merge_buffer.append(entry)
            if len(merge_buffer) >= MAX_MERGE_COUNT:
                _flush_buffer()
        elif content_len > LONG_THRESHOLD:
            # Flush any buffered entries first
            _flush_buffer()
            # Long entry → split
            sub_chunks = _split_long_entry(entry, global_chunk_idx)
            chunks.extend(sub_chunks)
            global_chunk_idx += len(sub_chunks)
        else:
            # Flush buffer, then add as medium
            _flush_buffer()
            chunks.append(_entry_to_chunk(entry, global_chunk_idx))
            global_chunk_idx += 1

    # Flush remaining buffer
    _flush_buffer()

    logger.info(
        "Built %d chunks: %d merged, %d standalone, %d split",
        len(chunks),
        sum(1 for c in chunks if c.is_merged),
        sum(1 for c in chunks if not c.is_merged and c.chunk_index == 0),
        sum(1 for c in chunks if c.chunk_index > 0),
    )
    return chunks


def _entry_to_chunk(entry: Entry, chunk_idx: int) -> Chunk:
    """Convert a single entry to a standalone chunk."""
    return Chunk(
        entry_id=entry.title,
        title=entry.title,
        category=entry.category,
        chunk_id=f"chunk_{chunk_idx:04d}",
        content=entry.content,
        image_ids=entry.image_ids,
        cross_refs=entry.cross_refs,
        merged_entries=[entry.title],
    )


def _merge_entries(
    entries: list[Entry], group_idx: int, chunk_idx: int
) -> Chunk:
    """Merge multiple short entries into one chunk."""
    titles = [e.title for e in entries]
    primary = titles[0]

    # Build merged content with entry markers
    parts = []
    all_images = []
    all_refs = []
    for e in entries:
        parts.append(f"【词条：{e.title_with_pinyin}】\n{e.content}")
        all_images.extend(e.image_ids)
        all_refs.extend(e.cross_refs)

    merged_content = "\n\n".join(parts)

    return Chunk(
        entry_id=primary,
        title=" / ".join(titles),
        category=entries[0].category,
        chunk_id=f"chunk_{chunk_idx:04d}",
        content=merged_content,
        image_ids=list(dict.fromkeys(all_images)),  # dedupe order-preserving
        cross_refs=list(dict.fromkeys(all_refs)),
        merged_entries=titles,
        is_merged=True,
    )


def _split_long_entry(entry: Entry, start_chunk_idx: int) -> list[Chunk]:
    """Split a genuinely long entry into sub-chunks at paragraph boundaries.

    Only splits entries > LONG_THRESHOLD. Group short paragraphs together
    to avoid too-small chunks.
    """
    content = _strip_images_from_content(entry.content)

    if len(content) <= LONG_THRESHOLD:
        # Content after image stripping is under threshold → single chunk
        return [_entry_to_chunk(entry, start_chunk_idx)]

    paragraphs = content.split('\n\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    if len(paragraphs) <= 1:
        # Single paragraph — force split at sentence boundaries
        sentences = re.split(r'(?<=[。！？])\s*', content)
        paragraphs = _group_sentences(sentences, MAX_CHUNK_SIZE)

    # Group small paragraphs into chunks
    groups = _group_paragraphs(paragraphs, MAX_CHUNK_SIZE, MIN_SPLIT_SIZE)

    if len(groups) <= 1:
        return [_entry_to_chunk(entry, start_chunk_idx)]

    chunks = []
    for i, para in enumerate(groups):
        chunks.append(Chunk(
            entry_id=entry.title,
            title=entry.title,
            category=entry.category,
            chunk_id=f"chunk_{start_chunk_idx + i:04d}",
            chunk_index=i,
            content=para,
            image_ids=entry.image_ids if i == 0 else [],
            cross_refs=entry.cross_refs,
            merged_entries=[entry.title],
        ))

    return chunks


def _group_paragraphs(
    paragraphs: list[str], max_size: int, min_size: int
) -> list[str]:
    """Group small paragraphs into chunks between min_size and max_size."""
    groups = []
    current = ""
    for para in paragraphs:
        # If adding this paragraph would exceed max, flush current
        if current and len(current) + len(para) > max_size:
            if len(current) >= min_size:
                groups.append(current.strip())
                current = para
            else:
                current += "\n\n" + para
        else:
            if current:
                current += "\n\n" + para
            else:
                current = para

        # If current is large enough, flush it
        if len(current) >= max_size:
            groups.append(current.strip())
            current = ""

    if current.strip():
        # Merge last small chunk into previous if too small
        if len(current) < min_size and groups:
            groups[-1] = groups[-1] + "\n\n" + current.strip()
        else:
            groups.append(current.strip())

    return groups


def _group_sentences(sentences: list[str], max_size: int) -> list[str]:
    """Group sentences into paragraphs not exceeding max_size."""
    groups = []
    current = ""
    for s in sentences:
        if len(current) + len(s) > max_size and current:
            groups.append(current.strip())
            current = s
        else:
            current += s
    if current.strip():
        groups.append(current.strip())
    return groups


# ============================================================================
# Step 3: Output
# ============================================================================

def build_page_mapping() -> dict[int, int]:
    """Build page_idx -> book page number mapping from content_list.json.

    The PDF-to-MD conversion pipeline produces a content_list.json that
    indexes every text block by page_idx (PDF page index). Book pages are
    recorded as page_number items on each page.

    Returns:
        Dict mapping page_idx to the actual book page number.
        Entries without a page number are omitted.
    """
    if not CONTENT_LIST_FILE.exists():
        logger.warning("content_list.json not found at %s, page numbers unavailable", CONTENT_LIST_FILE)
        return {}

    with open(CONTENT_LIST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    page_map: dict[int, int] = {}
    for item in data:
        if item.get("type") == "page_number":
            pid = item["page_idx"]
            pn = item.get("text", "").strip()
            # Book page number may be "18", "4/5" (facing pages), etc.
            if not pn:
                continue
            try:
                page_map[pid] = int(pn.split("/")[0])
            except ValueError:
                pass

    logger.info(
        "Page number mapping built: %d pages indexed, page_idx range [%d, %d]",
        len(page_map),
        min(page_map) if page_map else 0,
        max(page_map) if page_map else 0,
    )
    return page_map


def extract_entry_page_indices() -> list[tuple[str, int]]:
    """Extract ordered list of (cleaned_title, page_idx) for all entry headers.

    Each H2-level text block in content_list.json that has pinyin in its
    title is a dictionary entry header. We extract them in document order
    so they can be aligned with entries parsed from the MD file.

    Returns:
        Ordered list of (cleaned_title, page_idx) tuples.
    """
    if not CONTENT_LIST_FILE.exists():
        logger.warning("content_list.json not found, cannot extract entry pages")
        return []

    with open(CONTENT_LIST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries: list[tuple[str, int]] = []
    for item in data:
        if item.get("type") == "text" and item.get("text_level") == 2:
            text = item["text"].strip()
            # category headers and skip-titles have no pinyin
            if text in CATEGORIES or text in SKIP_TITLES:
                continue
            clean = _clean_title(text)
            if clean:
                entries.append((clean, item["page_idx"]))

    logger.info("Extracted %d entry headers with page indices from content_list", len(entries))
    return entries


def assign_pages_to_entries(
    md_entries: list[Entry],
    cl_entries: list[tuple[str, int]],
    page_map: dict[int, int],
) -> dict[str, int]:
    """Assign book page numbers to MD entries by positional alignment.

    The MD file and content_list.json are generated from the same source
    and preserve the same entry order. We walk through both lists,
    matching entries by cleaned title with a local search window.

    Args:
        md_entries: Entries parsed from the MD file (in order).
        cl_entries: (cleaned_title, page_idx) tuples from content_list (in order).
        page_map: page_idx -> book page number mapping.

    Returns:
        Dict mapping cleaned entry title to book page number.
    """
    if not page_map or not cl_entries:
        return {}

    result: dict[str, int] = {}
    cl_idx = 0
    window = 15  # search window for fuzzy alignment

    for entry in md_entries:
        title = _clean_title(entry.title_with_pinyin)
        matched_page: int | None = None

        # Attempt exact match within sliding window around current position
        for offset in range(-window, window + 1):
            check_idx = cl_idx + offset
            if 0 <= check_idx < len(cl_entries) and cl_entries[check_idx][0] == title:
                pid = cl_entries[check_idx][1]
                matched_page = page_map.get(pid)
                cl_idx = check_idx + 1
                break

        result[title] = matched_page

    matched = sum(1 for v in result.values() if v is not None)
    logger.info(
        "Page assignment: %d/%d entries matched (%.1f%%)",
        matched,
        len(result),
        100 * matched / max(len(result), 1),
    )
    return result


def chunks_to_dicts(
    chunks: list[Chunk],
    entry_pages: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    """Convert chunks to dicts suitable for Milvus insertion.

    Args:
        chunks: Chunk objects from the chunking pipeline.
        entry_pages: Optional mapping from cleaned entry title to book page
            number. If provided, real page numbers are used.

    Returns:
        List of dicts with keys matching the Milvus collection schema.
    """
    if entry_pages is None:
        entry_pages = {}

    return [
        {
            "entry_id": c.entry_id,
            "title": c.title,
            "page": _get_page_for_chunk(c, entry_pages),
            "chunk_id": c.chunk_id,
            "content": c.content,
        }
        for c in chunks
    ]


def _get_page_for_chunk(
    chunk: Chunk,
    entry_pages: dict[str, int],
) -> int:
    """Determine the page number for a chunk.

    For merged chunks, uses the first merged entry's page.
    For split chunks, all sub-chunks inherit the same page.
    Returns 0 if no page mapping is available.

    Args:
        chunk: The chunk to look up.
        entry_pages: Cleaned title -> page number mapping.

    Returns:
        Book page number, or 0 if not found.
    """
    # Try each merged entry title (cleaned) until we find a match
    for entry_title in chunk.merged_entries:
        # entry_title in merged_entries is already the clean title
        page = entry_pages.get(entry_title)
        if page is not None and page > 0:
            return page

    # Fallback: try the chunk's primary entry_id (also a clean title)
    page = entry_pages.get(chunk.entry_id)
    if page is not None and page > 0:
        return page

    return 0


def print_statistics(entries: list[Entry], chunks: list[Chunk]) -> None:
    """Print summary statistics."""
    print("\n" + "=" * 60)
    print("  知识库组织统计")
    print("=" * 60)

    # Category distribution
    cat_counts: dict[str, int] = {}
    for e in entries:
        cat_counts[e.category] = cat_counts.get(e.category, 0) + 1

    print(f"\n{'分类':<18} {'词条数':>6} {'图片':>5}")
    print("-" * 32)
    total_imgs = 0
    for cat in CATEGORIES:
        count = cat_counts.get(cat, 0)
        imgs = sum(len(e.image_ids) for e in entries if e.category == cat)
        total_imgs += imgs
        if count > 0:
            print(f"  {cat:<16} {count:>6} {imgs:>5}")
    print("-" * 32)
    print(f"  {'合计':<16} {len(entries):>6} {total_imgs:>5}")

    # Chunk statistics
    merged = sum(1 for c in chunks if c.is_merged)
    split = sum(1 for c in chunks if c.chunk_index > 0)
    standalone = len(chunks) - merged - split
    merged_entries = sum(len(c.merged_entries) for c in chunks if c.is_merged)

    print(f"\n{'Chunk统计':<18} {'数量':>6}")
    print("-" * 26)
    print(f"  {'独立词条(1:1)':<16} {standalone:>6}")
    print(f"  {'合并chunk':<16} {merged:>6}  (覆盖{merged_entries}个词条)")
    print(f"  {'长词条切分':<16} {split:>6}")
    print(f"  {'总计Chunk':<16} {len(chunks):>6}")

    sizes = [len(c.content) for c in chunks]
    print(f"\n  Chunk大小: min={min(sizes)}, max={max(sizes)}, "
          f"median={sorted(sizes)[len(sizes)//2]}, avg={sum(sizes)//len(sizes)}")


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Build knowledge chunks from dictionary MD")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse and chunk without inserting into Milvus",
    )
    parser.add_argument(
        "--json-output", type=str, default=None,
        help="Output chunks as JSON file",
    )
    parser.add_argument(
        "--stats-only", action="store_true",
        help="Only print statistics, no output",
    )
    args = parser.parse_args()

    # Step 1: Parse entries
    logger.info("Parsing dictionary entries from %s", MD_FILE)
    entries = parse_entries(MD_FILE)

    # Step 2: Build chunks
    logger.info("Building chunks...")
    chunks = build_chunks(entries)

    # Step 3: Extract page numbers from the PDF-to-MD intermediate data
    logger.info("Building page number mapping from content_list.json...")
    page_map = build_page_mapping()
    cl_entries = extract_entry_page_indices()
    entry_pages = assign_pages_to_entries(entries, cl_entries, page_map)

    # Step 4: Print statistics
    print_statistics(entries, chunks)

    if args.stats_only:
        return

    # Convert to dicts with real page numbers
    chunk_dicts = chunks_to_dicts(chunks, entry_pages)

    # JSON output
    json_path = args.json_output or str(DEFAULT_OUTPUT)
    output_path = Path(json_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save full chunk data (including metadata for debugging)
    full_data = []
    for c in chunks:
        d = {
            "entry_id": c.entry_id,
            "title": c.title,
            "page": _get_page_for_chunk(c, entry_pages),
            "category": c.category,
            "chunk_id": c.chunk_id,
            "chunk_index": c.chunk_index,
            "content": c.content,
            "image_ids": c.image_ids,
            "cross_refs": c.cross_refs,
            "merged_entries": c.merged_entries,
            "is_merged": c.is_merged,
        }
        full_data.append(d)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2)

    logger.info("Saved %d chunks to %s", len(full_data), output_path)

    # Save milvus-ingestable format
    milvus_path = output_path.parent / "chunks_milvus.json"
    with open(milvus_path, "w", encoding="utf-8") as f:
        json.dump(chunk_dicts, f, ensure_ascii=False, indent=2)
    logger.info("Saved %d Milvus-ready records to %s", len(chunk_dicts), milvus_path)

    if args.dry_run:
        logger.info("Dry run complete — no data inserted into Milvus")
        return

    # Step 5: Insert into Milvus
    logger.info("Inserting chunks into Milvus...")
    _insert_into_milvus(chunk_dicts)
    logger.info("Ingestion complete!")


def _insert_into_milvus(chunk_dicts: list[dict]) -> None:
    """Insert chunks into Milvus with BGE-M3 embeddings."""
    # Add backend to path
    backend_path = str(PROJECT_ROOT / "backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

    from app.embedding.embedding_service import EmbeddingService
    from app.database.milvus_client import MilvusConnectionManager
    from app.database.collection_setup import ensure_collection_exists

    # Ensure collection exists
    ensure_collection_exists()

    # Generate embeddings
    embedding_service = EmbeddingService()
    texts = [d["content"] for d in chunk_dicts]

    logger.info("Generating BGE-M3 embeddings for %d chunks...", len(texts))
    embeddings = embedding_service.encode(texts, show_progress_bar=True)

    # Attach embeddings to data — field must be named "vector" to match
    # the default MilvusClient.create_collection() schema.
    for i, emb in enumerate(embeddings):
        chunk_dicts[i]["vector"] = emb.tolist()

    # Insert into Milvus in batches
    milvus = MilvusConnectionManager()
    from app.config.settings import get_settings
    settings = get_settings()
    collection_name = settings.milvus_collection_name

    batch_size = 100
    total = len(chunk_dicts)
    for i in range(0, total, batch_size):
        batch = chunk_dicts[i:i + batch_size]
        milvus.client.insert(collection_name=collection_name, data=batch)
        logger.info("Inserted batch %d/%d (%d chunks)", i // batch_size + 1,
                     (total + batch_size - 1) // batch_size, len(batch))

    logger.info("Successfully inserted %d chunks into Milvus", total)


if __name__ == "__main__":
    main()
