PAGE_NAV = [
    ("ve-chung-toi", "Câu chuyện thương hiệu"),
    ("huong-dan-chon-size", "Hướng dẫn chọn size"),
    ("chinh-sach-doi-tra", "Chính sách đổi trả"),
    ("chat-lieu-bao-quan", "Chất liệu & bảo quản"),
    ("tuyen-dung", "Tuyển dụng"),
    ("lien-he", "Liên hệ"),
]

PAGES = {
    "ve-chung-toi": {
        "title": "Câu chuyện thương hiệu",
        "meta": "HUUGIAU Atelier — khám phá sản phẩm, thông tin kích cỡ và cách đặt hàng trên website.",
        "body_html": """
<p>HUUGIAU Atelier là website giới thiệu và nhận đơn hàng thời trang. Thông tin về giá, màu, kích cỡ và tình trạng còn hàng được hiển thị trên từng trang sản phẩm.</p>
<p>Bạn có thể xem sản phẩm, chọn biến thể, đặt hàng và theo dõi trạng thái đơn ngay trên website. Nếu cần xác nhận thông tin trước khi mua, hãy dùng kênh liên hệ được công bố tại <a href="/lien-he/">trang Liên hệ</a>.</p>
""",
    },
    "huong-dan-chon-size": {
        "title": "Hướng dẫn chọn size",
        "meta": "Cách đối chiếu số đo và thông tin kích cỡ trên từng sản phẩm HUUGIAU Atelier.",
        "body_html": """
<p>Kích cỡ có thể khác nhau giữa các sản phẩm. Hãy xem các size đang bán và bảng số đo riêng trên trang sản phẩm nếu đã được cung cấp; website không áp dụng một bảng số đo chung cho mọi mẫu.</p>
<h2>Cách đối chiếu</h2>
<ul>
<li>Đo một sản phẩm cùng loại bạn đang mặc vừa và đối chiếu từng số đo được công bố.</li>
<li>Nếu trang sản phẩm chưa có số đo, hãy liên hệ shop để xác nhận trước khi đặt hàng.</li>
<li>Chiều cao và cân nặng không đủ để xác định chính xác kích cỡ hoặc độ vừa của một mẫu cụ thể.</li>
</ul>
""",
    },
    "chinh-sach-doi-tra": {
        "title": "Chính sách đổi trả",
        "meta": "Cách gửi yêu cầu đổi trả và theo dõi xử lý đơn hàng tại HUUGIAU Atelier.",
        "body_html": """
<h2>Gửi yêu cầu</h2>
<p>Với đơn hàng được hệ thống ghi nhận đã giao thành công, tài khoản đã đặt hàng có thể gửi yêu cầu đổi hoặc hoàn tiền trong vòng <strong>7 ngày</strong> từ thời điểm giao hàng. Yêu cầu sẽ được nhân viên xem xét; gửi yêu cầu không đồng nghĩa với việc được duyệt hoặc hoàn tiền tự động.</p>
<ol>
<li>Đăng nhập và mở mục <a href="/don-hang-cua-toi/">Đơn hàng của tôi</a>.</li>
<li>Chọn đơn đã giao, gửi yêu cầu và mô tả lý do cùng sản phẩm liên quan.</li>
<li>Chờ shop xác nhận điều kiện và hướng dẫn bước tiếp theo. Đơn đặt không đăng nhập có thể dùng kênh liên hệ đã công bố để được hỗ trợ.</li>
</ol>
<p>Chi phí vận chuyển đổi trả, thời hạn xử lý và phương thức hoàn tiền chưa được công bố. Hãy xác nhận các điều kiện này với shop trước khi đặt hàng; website chưa tự động hoàn tiền.</p>
""",
    },
    "chat-lieu-bao-quan": {
        "title": "Chất liệu & bảo quản",
        "meta": "Hướng dẫn bảo quản chung; ưu tiên nhãn chăm sóc và thông tin của từng sản phẩm.",
        "body_html": """
<p>Thành phần vải và hướng dẫn chăm sóc có thể khác nhau theo sản phẩm. Ưu tiên thông tin trên nhãn và trang chi tiết của đúng sản phẩm bạn nhận được.</p>
<h2>Lưu ý chung</h2>
<ul>
<li>Phân loại màu và kiểm tra nhãn trước khi giặt hoặc sấy.</li>
<li>Thử cách làm sạch ở vùng nhỏ, khó thấy nếu chưa rõ đặc tính chất liệu.</li>
<li>Không tự áp dụng cùng một nhiệt độ hoặc hóa chất cho mọi loại vải.</li>
</ul>
""",
    },
    "tuyen-dung": {
        "title": "Tuyển dụng",
        "meta": "Thông tin tuyển dụng của HUUGIAU Atelier khi có vị trí được xác nhận.",
        "body_html": """
<p>Hiện website chưa công bố vị trí tuyển dụng đã được xác nhận. Khi có thông tin chính thức, nội dung sẽ được cập nhật tại đây.</p>
""",
    },
    "chinh-sach-bao-mat": {
        "title": "Chính sách bảo mật",
        "meta": "Thông tin dữ liệu hiện có trên website HUUGIAU Atelier; chính sách bảo mật chính thức đang được xác nhận.",
        "body_html": """
<p>Chính sách bảo mật chính thức chưa được chủ shop xác nhận. Phần dưới đây mô tả các loại dữ liệu website dùng trong những chức năng hiện có.</p>
<h2>Dữ liệu bạn cung cấp</h2>
<ul>
<li>Khi tạo tài khoản hoặc đặt hàng, website lưu thông tin bạn nhập như tên, email, số điện thoại và địa chỉ giao hàng.</li>
<li>Website lưu sản phẩm đã đặt, số tiền, phương thức thanh toán và trạng thái đơn để xử lý và tra cứu đơn.</li>
</ul>
<p>Thời gian lưu trữ, bên nhận dữ liệu và quy trình xử lý yêu cầu dữ liệu cá nhân cần được chủ shop xác nhận trước khi công bố chính sách đầy đủ.</p>
<p>Nếu cần trao đổi về dữ liệu của mình, hãy dùng kênh hỗ trợ đã được công bố tại <a href="/lien-he/">trang Liên hệ</a>.</p>
""",
    },
    "dieu-khoan": {
        "title": "Điều khoản sử dụng",
        "meta": "Cách sử dụng website và đặt hàng hiện có tại HUUGIAU Atelier; điều khoản thương mại đang được xác nhận.",
        "body_html": """
<p>Điều khoản thương mại chính thức chưa được chủ shop xác nhận. Những nội dung dưới đây mô tả cách website đang hoạt động.</p>
<h2>Sản phẩm và đơn hàng</h2>
<ul>
<li>Trang sản phẩm hiển thị thông tin, giá và biến thể đang được shop nhập vào hệ thống.</li>
<li>Trước khi xác nhận đặt hàng, bạn có thể kiểm tra sản phẩm, phí vận chuyển và tổng tiền ở bước thanh toán.</li>
<li>Sau khi đặt, bạn có thể tra cứu trạng thái đơn bằng chức năng trên website.</li>
</ul>
<p>Điều kiện xác nhận hoặc hủy đơn, đổi trả và hoàn tiền cần được chủ shop chốt trước khi công bố. Nếu cần làm rõ trước khi mua, hãy dùng kênh đã xác minh tại <a href="/lien-he/">trang Liên hệ</a>.</p>
""",
    },
    "lien-he": {
        "title": "Liên hệ",
        "meta": "Các kênh liên hệ và hỗ trợ của HUUGIAU Atelier.",
        "body_html": """
<h2>Hỗ trợ khách hàng</h2>
<p>Kênh hỗ trợ và địa chỉ nhận khách, nếu đã được xác minh, được công bố ở chân trang. Bạn cũng có thể tra cứu trạng thái đơn trên website.</p>
<h2>Tra cứu đơn hàng</h2>
<p>Đã đặt hàng? Dùng <a href="/tra-cuu-don/">Tra cứu đơn hàng</a> để theo dõi trạng thái, hoặc kiểm tra trong <a href="/don-hang-cua-toi/">Đơn hàng của tôi</a> nếu đã đăng nhập.</p>
""",
    },
}

META_FALLBACK = "HUUGIAU Atelier — streetwear local gọn, dễ mặc, đủ điểm nhấn."
