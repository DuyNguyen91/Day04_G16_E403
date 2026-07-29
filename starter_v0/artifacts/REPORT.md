# Day 04 Lab v2 Report — Research Agent

> File này tổng hợp lại tiến trình tối ưu agent từ baseline đến các phiên bản v0–v3, kèm bằng chứng từ eval và transcript thực tế.

## Team

- Team: G16 / E403
- Members: Group 16
- Provider/model: OpenRouter / combo3

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Agent này có thể hỗ trợ tra cứu thông tin nghiên cứu: tìm tweet theo tài khoản hoặc chủ đề, tìm tin tức/web, đọc URL cụ thể, hỏi lại khi thiếu thông tin, và thực hiện xác nhận trước các hành động gửi/đăng. Ở phiên bản nhóm, agent còn có thể gọi thêm các tool mở rộng như YouTube summarizer, weather forecast, crypto tracker, GitHub explorer và image generator.

**Link dùng thử (truy cập được trong showdown):**

> URL: demo local / chưa public; có thể chạy trực tiếp từ thư mục project bằng môi trường hiện tại.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại khi thiếu handle, URL hoặc cần xác nhận trước khi gửi | không |
| timeline | lấy tweet/bài đăng gần đây của một tài khoản X | không |
| social_search | tìm tweet theo chủ đề | không |
| lookup | tìm tin tức/web theo từ khóa và timeframe | không |
| fetch | đọc nội dung từ một URL cụ thể | không |
| format | tổng hợp kết quả thành câu trả lời có cấu trúc | không |
| send | chuẩn bị hành động gửi/đăng sau khi được xác nhận | không |
| youtube_summarizer | tóm tắt video YouTube từ URL | có |
| weather_forecast | trả lời thời tiết cho một địa điểm | có |
| crypto_tracker | tra cứu giá coin theo symbol | có |
| github_explorer | tìm repo/project GitHub theo từ khóa và ngôn ngữ | có |
| image_generator | tạo hình ảnh từ mô tả văn bản | có |

## A3. Câu hỏi mẫu để thử

1. "Tin tức AI hôm nay có gì nổi bật?"
2. "Tweet mới nhất của Sam Altman là gì?"
3. "Tóm tắt video youtube này giúp mình: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
4. "Thời tiết ở Tokyo hôm nay thế nào?"
5. "Đăng bản tin này lên Telegram giúp mình"

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Tin tức hôm nay | lookup(topic=news, timeframe=day) | Từ v0 bị dùng query quá dài, v1–v3 đã ổn hơn | [runs/v3_B_base_openrouter_20260729T112819185449.json](runs/v3_B_base_openrouter_20260729T112819185449.json) |
| Tóm tắt video | youtube_summarizer(url=...) | Tool mới nhóm thêm, đã được validate trong eval nhóm | [data/eval_group.json](data/eval_group.json) |
| Xác nhận trước khi gửi | clarify(response_type=yes_no) | V1–v3 đã bắt được boundary này rõ hơn | [runs/v2_B_base_openrouter_20260729T112105279945.json](runs/v2_B_base_openrouter_20260729T112105279945.json) |
| Chuyển từ Github sang web/news | github_explorer → lookup(topic=news) | Đã được xử lý tốt trong case multi-turn nhóm | [data/eval_group.json](data/eval_group.json) |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: provider_error_cases = 0; measured_cases = total_cases; và với các case có tool_results lỗi thì cần review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | Baseline, tool descriptions còn mơ hồ | Agent cần quy tắc routing rõ hơn cho timeline/social/lookup và clarify | case_accuracy | — | 0.60 | [runs/v0_B_base_openrouter_20260729T102815721595.json](runs/v0_B_base_openrouter_20260729T102815721595.json) |
| v1 | Bổ sung quy tắc routing trong [artifacts/system_prompt.md](artifacts/system_prompt.md) và [artifacts/tools.yaml](artifacts/tools.yaml) | Agent sẽ hỏi lại khi thiếu handle/URL và dùng lookup đúng cho web/news | case_accuracy | 0.60 | 0.95 | [runs/v1_B_base_openrouter_20260729T111051351225.json](runs/v1_B_base_openrouter_20260729T111051351225.json) |
| v2 | Làm rõ boundary xác nhận trước khi gửi và rule chuyển từ Twitter sang web/news | Agent sẽ dùng clarify yes_no cho send/post và không lẫn lẫn tool | case_accuracy | 0.95 | 0.80 | [runs/v2_B_base_openrouter_20260729T112105279945.json](runs/v2_B_base_openrouter_20260729T112105279945.json) |
| v3 | Tinh chỉnh thêm cho missing URL và confirmation boundary; bổ sung tool mới cho eval nhóm | Agent sẽ ổn định hơn ở cả base và group eval | case_accuracy | 0.80 | 0.90 | [runs/v3_B_base_openrouter_20260729T112819185449.json](runs/v3_B_base_openrouter_20260729T112819185449.json) |

## B2. Failure analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R11_missing_url | missing_info | none | Agent không gọi clarify khi user nói “bài này” mà chưa có URL | Thêm rule trong prompt: nếu user đề cập “bài này/ bài viết này” mà chưa có URL thì phải hỏi lại bằng clarify(text) |
| R12_confirm_before_send | wrong_boundary | clarify(response_type=text) | Agent hiểu nhầm “đăng lên Telegram” là thiếu thông tin thay vì confirmation boundary | Thêm rule rõ: send/post là yes_no confirmation, không hỏi lại nội dung nếu nội dung đã có trong request |
| M06_switch_tool | wrong_tool | social_search | Agent không chuyển sang lookup khi user đổi ý từ Twitter sang web/news | Thêm rule: nếu user explicitly chuyển sang web/news, ưu tiên lookup(topic=news) |
| M10_crypto_to_telegram | wrong_boundary | none | Agent không gọi clarify cho hành động gửi tin nhắn | Dùng cùng rule confirmation boundary cho send/post trong prompt và tools.yaml |

## B3. Team eval cases

Danh sách 10 case do nhóm tự viết trong [data/eval_group.json](data/eval_group.json): 5 single-turn và 5 multi-turn.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| T01_youtube_summarizer_single | URL YouTube hợp lệ → gọi youtube_summarizer | youtube_summarizer(url=...) | Pass |
| T02_weather_forecast_single | Hỏi thời tiết ở một thành phố | weather_forecast(location=Tokyo) | Pass |
| T03_crypto_tracker_single | Tra giá coin theo symbol | crypto_tracker(symbol=ETH) | Pass |
| T04_github_explorer_single | Tìm repo trên GitHub | github_explorer(query=AI, language=Python) | Pass |
| T05_image_generator_single | Yêu cầu tạo ảnh | image_generator(prompt=...) | Pass |
| M07_youtube_missing_url | Thiếu URL khi yêu cầu tóm tắt video | clarify(response_type=text) | Pass |
| M08_youtube_provide_url | Sau khi được URL, gọi đúng tool tóm tắt | youtube_summarizer(url=...) | Pass |
| M09_weather_follow_up | Hiểu ngữ cảnh từ lượt trước | weather_forecast(location=Paris) | Pass |
| M10_crypto_to_telegram | Xác nhận trước khi gửi tin nhắn Telegram | clarify(response_type=yes_no) | Fail in v3 run; boundary rule cần tiếp tục cải thiện |
| M11_switch_tool_github_to_news | Chuyển từ Github sang web/news | lookup(query=React 19, topic=news) | Pass |

## B4. Live chat evidence

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Tin AI hôm nay | v3 | lookup(query=AI, topic=news, timeframe=day) | [samples/transcripts/example_openrouter_20260101T030000000000.transcript.json](samples/transcripts/example_openrouter_20260101T030000000000.transcript.json) | Pass |
| Câu hỏi thiếu thông tin | v3 | clarify(response_type=text) | [samples/transcripts/example_openrouter_20260101T030000000000.transcript.json](samples/transcripts/example_openrouter_20260101T030000000000.transcript.json) | Pass |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên | [tools/youtube_summarizer/TOOL.md](tools/youtube_summarizer/TOOL.md) | Route đúng cho URL video và gọi tool tóm tắt | Hiện là stub/local, chưa tích hợp YouTube API thật |
| Optional built-in | [tools/lookup/TOOL.md](tools/lookup/TOOL.md) | Tìm tin tức/web đúng theo topic và timeframe | Cần tránh query dài quá mức và giữ query ngắn |
| Bonus: tool mới thứ 4 trở đi | [tools/github_explorer/TOOL.md](tools/github_explorer/TOOL.md), [tools/image_generator/TOOL.md](tools/image_generator/TOOL.md) | Có thể bật được cho các case nhóm và giữ routing rõ ràng | Các implementation hiện tại là stub, phù hợp cho lab hơn là production |

## B6. Reflection

- Các fix thuộc về [artifacts/system_prompt.md](artifacts/system_prompt.md): quy tắc hỏi lại khi thiếu URL, quy tắc confirmation boundary cho send/post, và quy tắc ưu tiên lookup khi user chuyển sang web/news.
- Các fix thuộc về [artifacts/tools.yaml](artifacts/tools.yaml): làm rõ schema của clarify, timeline, social_search và lookup, đồng thời khai báo các tool mới cho eval nhóm.
- Failure cần review thủ công thay vì chỉ dựa vào grading tự động là các trường hợp tool execution thực tế có lỗi nội bộ hoặc tool result không ổn định; ví dụ các case liên quan đến send/post và tool runtime chưa được tích hợp thật.
- Điểm cải thiện tiếp theo: tích hợp thật các tool mới (YouTube/GitHub/Weather/Crypto/Image), thêm few-shot examples cho confirmation boundary, và đánh giá lại với transcript thực tế để giảm lỗi false-positive trong multi-turn.
