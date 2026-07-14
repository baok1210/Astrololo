# Tích hợp kho kiến thức "crawl kiến thức astro" vào Astrololo

> Khảo sát ngày 14/07/2026 · Đánh giá tính khả thi tích hợp.

## 1. Kho dữ liệu nằm ở đâu
- `C:\Users\BabaBun\Downloads\crawl kiến thức astro\data\markdown\` — **997 file .md**, ~5.8 MB, 105 MB cả thư mục (gồm cả DB + json).
- Không phải `Downloads/crawl` hay `Astrololo/data/` (hai đường dẫn đó không tồn tại) — thư mục thực tế có dấu cách trong tên.
- Nguồn: `cafe_astrology` (442), `astrosage` (516), `astro_com` (3), `www_astrologyland_com` (36).
- `Downloads/data/` (rỗng markdown) và `Astrololo.rar` (backup 54MB) không chứa KB này.

## 2. Cấu trúc & chất lượng (RẤT TỐT để tích hợp)
Mỗi file có YAML frontmatter chuẩn:
```
---
title: "..."
url: "https://cafeastrology.com/..."
source: "cafe_astrology"
category: "planets"        # planets / aspects / houses / zodiac / compatibility / nodes
subcategory: ""
crawled_at: "2026-06-16T..."
---
# Heading ...
Prose sạch, dài 1-6KB, tiếng Anh.
```
Phân loại khớp **chính xác** với 19 dimension Astrololo đang interpret:
`planet_*_sign`, `planet_*_house`, `aspects`, `houses`, `zodiac_signs`,
`north_node_signs`, `love_compatibility`, `predictive`, `chiron`.

→ Đây là corpus tiếng Anh tham khảo chất lượng cao, bổ sung trực tiếp cho nhánh **EN**
(hiện Astrololo EN dựa vào scraping cũ + fallback từ khóa VI).

## 3. Seam đã có sẵn trong code
`astrololo/interpretation/knowledge_base.py` đã có cơ chế:
- env `ASTRO_KNOWLEDGE_BASE` → folder chứa `_synthesis/` (sign/planet synthesis VI).
- `enrich_planet_in_sign()`, `enrich_planet_in_house()`, `is_kb_available()`.
- Nhưng đường dẫn mặc định trỏ tới `C:\Users\Admin\Downloads\Chiêm tinh kiến thức`
  (không tồn tại trên máy này) → KB hiện **không hoạt động**.

Điểm nghẽn: module hiện chỉ đọc định dạng `_synthesis/*.md` (VI, hand-made),
chưa đọc được corpus `markdown/` (EN, frontmatter + prose).

## 4. Đánh giá: CÓ THỂ tích hợp không? → CÓ, 3 mức

### Mức A — Nhanh (1-2h): Retriever "RAG nhẹ" cho EN
Thêm `astrololo/interpretation/knowledge_retriever.py`:
- Load toàn bộ 997 .md vào index (source + category + subcategory + text).
- Hàm `retrieve(planet, sign)` / `retrieve(planet, house)` / `retrieve(aspect_type)`
  trả về đoạn prose EN phù hợp (match theo category/subcategory + keyword).
- Gọi trong `template_loader.get_planet_in_sign(lang="en")` để **thay thế/thêm**
  đoạn prose EN thực tế thay vì fallback từ khóa.
- Bật qua env `ASTRO_KB_MARKDOWN=<đường dẫn markdown>`.
→ Tăng vượt trội chất lượng EN (đúng ý nghĩa cafeastrology) mà không phá VI.

### Mức B — Trung bình: Map corpus → template YAML EN
Viết script `scripts/import_crawl_kb.py`: parse 997 file, group theo
`category/subcategory`, sinh `templates/en/planet_in_sign.yaml` mở rộng
(planet×sign), `planet_in_house.yaml`, `aspects.yaml` bổ sung.
→ Đồng bộ với pipeline template hiện tại, có thể review/diff an toàn.

### Mức C — Đầy đủ: Vector search (FAISS/SQLite-vss)
Nếu muốn "hỏi đáp" (AI/luận giải theo yêu cầu) thì embedding + similarity.
Nặng hơn, chỉ cần nếu làm tính năng chat. **Không bắt buộc** để vượt web astro.

## 5. Rủi ro / lưu ý
- Bản quyền: cafeastrology/astro.com có ToS cấm scrape-thương mại. Dùng nội bộ /
  cá nhân OK; nếu deploy công khai cần check license hoặc chỉ lấy đoạn trích ngắn.
- Trùng lặp: astrosage (516) có thể trùng ý với cafe_astrology → cần dedupe theo (title,source).
- Tiếng Việt: corpus là EN. Nhánh VI vẫn dùng template VI có sẵn (đã 147+ test).
  Nếu muốn VI từ corpus EN → cần translate (không có API key hiện tại).

## 6. Đề xuất
Làm **Mức A trước** (retriever EN nhẹ, tách biệt, bật bằng env) vì:
- Tận dụng 100% 997 file không cần transform.
- Không động vào pipeline cũ → không gãy 156 test.
- EN lập tức sánh ngang cafeastrology (nguồn gốc của corpus).
Sau đó tuỳ phản hồi mới làm Mức B (commit vào YAML) hoặc C.
