# King Volleyball — hướng dẫn chạy và kiểm tra

## 1. Chạy local trên Windows

Mở PowerShell tại thư mục có `manage.py`:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py runserver
```

Mở `http://127.0.0.1:8000/`. Trang đăng nhập: `/login/`; trang đăng ký: `/register/`; trang quản trị: `/admin/`.

Nếu PowerShell chặn kích hoạt môi trường ảo, có thể dùng `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` trong cửa sổ terminal hiện tại rồi kích hoạt lại.

## 2. Tài khoản quản trị (Admin)

Tài khoản quản trị mặc định đã được cấu hình sẵn trong hệ thống:
- **Tên đăng nhập (Username):** `admin`
- **Mật khẩu (Password):** `admin123`
- **Quyền:** Quản trị viên tối cao (Superuser / Staff)
- **Đăng nhập quản trị:** Truy cập `http://127.0.0.1:8000/admin/` hoặc đăng nhập tại `/login/` (tài khoản admin sẽ có thêm menu "Thêm sản phẩm" và "Quản trị" trên thanh điều hướng).

Nếu bạn muốn tạo thêm tài khoản quản trị mới khác:

```powershell
python manage.py createsuperuser
```

## 3. Chạy bằng Docker

Cần cài và mở Docker Desktop trước:

```powershell
docker compose up --build
```

Mở `http://127.0.0.1:8000/`. Dừng container bằng `Ctrl+C`; nếu chạy nền thì dùng `docker compose down`.

## 4. Các thay đổi chính

- Làm mới giao diện đăng nhập/đăng ký, co giãn trên điện thoại, thêm hiện/ẩn mật khẩu và thông báo lỗi.
- Bổ sung kiểm tra email đã được dùng, dùng validator mật khẩu mặc định của Django.
- Sửa đường dẫn static CSS, sửa tên biến flash sale và biến phần trăm giảm giá trong trang chủ.
- Sửa route đánh giá sản phẩm để nhận `product_id`.
- Giới hạn thao tác xóa khỏi giỏ và thanh toán mục đã chọn theo người dùng đăng nhập.
- Thêm `requirements.txt`, `Dockerfile`, `docker-compose.yml` và `.dockerignore` để phục vụ thực hành DevOps.

## 5. Lưu ý trước khi nộp/deploy

Cấu hình Docker hiện dùng Django development server và `DEBUG=1` để thuận tiện thực hành giữa kỳ, **không dùng trực tiếp cho production**. Trước khi public lên Internet, hãy đặt `DJANGO_DEBUG=0`, đặt `DJANGO_SECRET_KEY` mạnh qua biến môi trường, cấu hình `ALLOWED_HOSTS`, HTTPS, static files và máy chủ WSGI phù hợp. Không commit secrets lên GitHub.
