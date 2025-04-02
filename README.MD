# GITHUB CONTROLLER API

## 1. NỘI DUNG 
Đây là API phục vụ lấy toàn diện các thông tin từ GitHub như cấu trúc repository, nội dung file, lịch sử commit và các thay đổi trong mã nguồn. API cũng tích hợp khả năng chat với các mô hình AI khác nhau.

## 2. HƯỚNG DẪN SỬ DỤNG

### 2.1. Cài đặt

1. Cài đặt các gói phụ thuộc:
   ```
   pip install -r requirements.txt
   ```

2. Cấu hình file `.env`:
   - GITHUB_TOKEN: Token truy cập GitHub của bạn
   - OPENAI_TOKEN: Token OpenAI API (nếu sử dụng tính năng chat)
   - CLAUDE_TOKEN: Token Claude API (nếu sử dụng)
   - DEEPSEEK_TOKEN: Token DeepSeek API (nếu sử dụng)
   - GEMINI_TOKEN: Token Gemini API (nếu sử dụng)
   - SUPER_USER_TOKEN: Token xác thực cho người dùng đặc biệt

3. Chạy ứng dụng:
   ```
   ./run.sh
   ```
   hoặc
   ```
   uvicorn main:app
   ```

### 2.2. Các API Endpoints

API được triển khai với tiền tố `/api/v1` và bao gồm các endpoint sau:

#### 2.2.1. Chat với AI
```
POST /api/v1/chat
```

**Tham số:**
- prompt: Chuỗi prompt gửi đến AI
- provider: Nhà cung cấp AI (OpenAI, Claude, DeepSeek, Gemini)
- model_name: Tên mô hình AI cụ thể
- history: Lịch sử cuộc trò chuyện (không bắt buộc)

**Kết quả:** Phản hồi từ mô hình AI được chọn

#### 2.2.2. Lấy thông tin các branch
```
POST /api/v1/branch
```

**Tham số:**
- repo_name: Tên repository trên GitHub
- access_token: Token truy cập GitHub (tự động từ xác thực)
- default: Chỉ lấy branch mặc định (true/false, mặc định là false)

**Kết quả:** Danh sách các branch của repository

#### 2.2.3. Lấy cấu trúc dạng cây của repository
```
POST /api/v1/structure
```

**Tham số:**
- repo_name: Tên repository
- branch: Tên branch (không bắt buộc, mặc định là branch mặc định)
- access_token: Token truy cập GitHub (tự động từ xác thực)

**Kết quả:** Cấu trúc dạng cây của repository hoặc lỗi 404 nếu không tìm thấy

#### 2.2.4. Lấy nội dung các file
```
POST /api/v1/get_content
```

**Tham số:**
- repo_name: Tên repository
- branch: Tên branch
- access_token: Token truy cập GitHub (tự động từ xác thực)
- files: Danh sách đường dẫn file cần lấy nội dung (không bắt buộc)
- forbidden_extensions: Danh sách các định dạng file không muốn lấy (không bắt buộc)

**Kết quả:** Nội dung của các file được yêu cầu

#### 2.2.5. Lấy lịch sử commit
```
POST /api/v1/get_commit_history
```

**Tham số:**
- repo_name: Tên repository
- branch: Tên branch (không bắt buộc)
- file_path: Đường dẫn đến file cụ thể (không bắt buộc)
- access_token: Token truy cập GitHub (tự động từ xác thực)

**Kết quả:** Lịch sử commit của repository hoặc file cụ thể

#### 2.2.6. Tổng hợp nội dung thay đổi qua các commit
```
POST /api/v1/get_changes
```

**Tham số:**
- repo_name: Tên repository
- branch: Tên branch (không bắt buộc)
- file_path: Đường dẫn đến file/thư mục cần xem thay đổi (không bắt buộc)
- commit_id: ID của commit cụ thể (không bắt buộc)
- access_token: Token truy cập GitHub (tự động từ xác thực)

**Kết quả:** Nội dung thay đổi theo yêu cầu

### 2.3. Ví dụ sử dụng

#### Lấy cấu trúc repository:
```
curl -X POST "http://localhost:8000/api/v1/structure" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_access_token" \
     -d '{"repo_name": "username/repository", "branch": "main"}'
```

#### Lấy nội dung file:
```
curl -X POST "http://localhost:8000/api/v1/get_content" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your_access_token" \
     -d '{"repo_name": "username/repository", "branch": "main", "files": ["path/to/file.py"]}'
```

### 2.4. Lưu ý

- Tất cả các API endpoints đều yêu cầu token xác thực GitHub
- Một số tính năng có thể yêu cầu các quyền đặc biệt trên GitHub repository
- Để sử dụng tính năng chat, bạn cần cung cấp API token tương ứng với nhà cung cấp AI

## 3. GIAO DIỆN NGƯỜI DÙNG

API này đi kèm với giao diện Swagger UI, có thể truy cập tại:
```
http://localhost:8000/docs
```

Giao diện này cho phép bạn:
- Khám phá tất cả các endpoints có sẵn
- Thử nghiệm các API trực tiếp từ trình duyệt
- Xem tài liệu chi tiết của từng endpoint

