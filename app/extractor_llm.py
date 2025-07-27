import fitz  # PyMuPDF
import json
from langdetect import detect
from collections import Counter
from pathlib import Path

def extract_text_with_fonts(pdf_path):
    doc = fitz.open(pdf_path)
    text_blocks = []
    font_metadata = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    size = span["size"]
                    text = span["text"].strip()
                    font = span["font"]
                    flags = span["flags"]  # bold/italic info
                    if not text:
                        continue
                    text_blocks.append({
                        "text": text,
                        "font_size": size,
                        "font": font,
                        "flags": flags,
                        "page": page_num + 1,
                        "bbox": span["bbox"]
                    })
                    font_metadata.append(size)
    return text_blocks, font_metadata

def infer_heading_levels(text_blocks, font_sizes):
    font_size_counts = Counter(font_sizes)
    common_sizes = [size for size, count in font_size_counts.items() if count > 5]
    sorted_sizes = sorted(common_sizes, reverse=True)
    heading_levels = {size: f"H{i+1}" for i, size in enumerate(sorted_sizes)}
    headings = []
    seen = set()
    for block in text_blocks:
        text = block["text"]
        size = block["font_size"]
        page = block["page"]
        flags = block["flags"]
        if len(text) < 3 or not any(c.isalpha() for c in text):
            continue
        key = (text.lower(), size)
        if key in seen or text.lower().startswith(("page", "figure", "table", "continued")):
            continue
        seen.add(key)
        words = text.split()
        is_short = len(words) <= 10
        is_bold = flags in [2, 3]  # 2: bold, 3: bold italic
        level = heading_levels.get(size)
        if not level:
            continue
        if is_bold or is_short:
            headings.append({
                "text": text,
                "level": level,
                "page": page
            })
    return headings

def detect_document_language(text_blocks):
    sample_text = " ".join([block["text"] for block in text_blocks[:50]])
    try:
        lang = detect(sample_text)
    except:
        lang = "unknown"
    return lang

def build_hierarchy(headings):
    outline = []
    stack = []
    def level_to_number(level):
        return int(level[1:])
    for item in headings:
        current_level = level_to_number(item["level"])
        node = {"text": item["text"], "level": item["level"], "page": item["page"]}
        text_strip = node["text"].strip()
        is_bullet = text_strip.startswith(tuple(["●", "○", "-", "*", "•"]))
        if is_bullet and stack:
            parent = stack[-1][1]
            if "children" not in parent:
                parent["children"] = []
            bullet_text = text_strip[1:].strip() if len(text_strip) > 1 else text_strip
            parent["children"].append({"text": bullet_text, "level": "bullet"})
            continue
        while stack and stack[-1][0] >= current_level:
            stack.pop()
        if not stack:
            outline.append(node)
            stack.append((current_level, node))
        else:
            parent = stack[-1][1]
            if "children" not in parent:
                parent["children"] = []
            parent["children"].append(node)
            stack.append((current_level, node))
    return outline

def post_process_outline(outline):
    """Merge label+description pairs, group bullets, attach descriptions."""
    def is_label_line(text):
        return text and not text[0] in ':.-•' and not text.endswith('.')
    def is_description_line(text):
        t = text.strip()
        return t.startswith(':') or (t and t[0].islower())
    def merge_label_description(children):
        merged = []
        skip = False
        for j in range(len(children)):
            if skip:
                skip = False
                continue
            current = children[j]
            next_c = children[j+1] if j+1 < len(children) else None
            if next_c and current['level'] in ('H3','H4') and next_c['level'] in ('H3','bullet'):
                if is_label_line(current['text']) and is_description_line(next_c['text']):
                    current['text'] = f"{current['text']} {next_c['text'].lstrip(':').strip()}"
                    merged.append(current)
                    skip = True
                else:
                    merged.append(current)
            else:
                merged.append(current)
        return merged
    def group_bullets(children):
        if not children: return children
        grouped=[]; bullets_group=[]
        def flush_bullets():
            nonlocal bullets_group
            if bullets_group:
                grouped.append({'bullets': [b['text'] for b in bullets_group]})
                bullets_group=[]
        for c in children:
            if c.get('level') == 'bullet':
                bullets_group.append(c)
            else:
                flush_bullets()
                grouped.append(c)
        flush_bullets()
        return grouped
    def is_continuation(text):
        t = text.strip()
        return t.startswith(':') or (t and t[0].islower())
    def recurse(nodes):
        merged_nodes=[]
        i=0
        while i<len(nodes):
            node=nodes[i]
            children = node.get('children')
            if children:
                node['children'] = recurse(children)
                node['children'] = merge_label_description(node['children'])
                node['children'] = group_bullets(node['children'])
            # label+desc merge at this level
            if i+1<len(nodes):
                next_node = nodes[i+1]
                if (node['level'] in ('H2', 'H3', 'H4') and next_node['level'] in ('H3', 'H4', 'bullet')):
                    if is_label_line(node['text']) and is_description_line(next_node['text']):
                        node['text'] = f"{node['text']} {next_node['text'].lstrip(':').strip()}"
                        i+=1
                    else:
                        merged_nodes.append(node)
                else:
                    merged_nodes.append(node)
            else:
                merged_nodes.append(node)
            i+=1
        # Attach continuation lines as descriptions
        final_nodes=[]
        for idx, nd in enumerate(merged_nodes):
            if idx>0 and is_continuation(nd['text']) and nd.get('level')!='bullet':
                prev=final_nodes[-1]
                if 'description' in prev:
                    prev['description'] += ' '+nd['text'].lstrip(':').strip()
                else:
                    prev['description'] = nd['text'].lstrip(':').strip()
            else:
                final_nodes.append(nd)
        return final_nodes
    return recurse(outline)

def generate_outline(pdf_path):
    text_blocks, font_sizes = extract_text_with_fonts(pdf_path)
    lang = detect_document_language(text_blocks)
    headings = infer_heading_levels(text_blocks, font_sizes)
    hierarchical_outline = build_hierarchy(headings)
    processed_outline = post_process_outline(hierarchical_outline)
    title = ""
    for h in headings:
        if h["level"] == "H1":
            title = h["text"]
            break
    return {
        "title": title if title else "Untitled Document",
        "language": lang,
        "outline": processed_outline
    }

if __name__ == "__main__":
    input_dir = Path("input")
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    for pdf_file in input_dir.glob("*.pdf"):
        outline = generate_outline(str(pdf_file))
        output_json_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_json_file, "w", encoding='utf-8') as f:
            json.dump(outline, f, indent=2, ensure_ascii=False)
        print(f"Processed '{pdf_file.name}' → '{output_json_file.name}'")
