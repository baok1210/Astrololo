from typing import List, Dict

PLANET_FUNCTIONS_VI: Dict[str, str] = {
    "sun": "Mặt Trời đem lại sức sống, lẽ sống, năng lượng sống, động lực sống, tình yêu, niềm vui, sự hào hứng, sự nhiệt tình, sự nổi bật, sức hấp dẫn. Là điều kiện để tất cả những hoạt động khác có thể diễn ra một cách có ý nghĩa. Đại diện cho người mà ta ngưỡng mộ, hình mẫu ta muốn trở thành, người truyền cảm hứng sống và niềm vui.",
    "moon": "Mặt Trăng là dấu ấn nghiệp về sự che chở, định nghĩa về con người hay nơi chốn đem lại cảm giác an toàn. Cách xử lý các dạng cảm xúc, tâm trạng, hành vi, cách giúp đỡ trấn an vỗ về. Bản năng tự vệ, phản ứng tự vệ, phản xạ vô điều kiện. Đại diện cho người mẹ lý tưởng, người bảo vệ che chở, chỗ dựa, nơi chốn bình yên.",
    "mercury": "Sao Thủy quản lý tư duy, hoạt động trí óc, tâm trí, cách lý giải đứng sau hoạt động nói và viết, khả năng học hỏi, tự tìm ra thông tin mới từ hiểu biết sẵn có. Là phương tiện liên kết giữa kí ức và hiện tại, đem đến cảm giác hiểu rõ hay hiểu ra một vấn đề. Đại diện cho anh chị em, người đương thời, nhà văn, nhà báo, giới trí thức.",
    "venus": "Sao Kim là dấu ấn nghiệp về nơi cá nhân từng nhận được sự thuận lợi hay hỗ trợ nho nhỏ hoặc cơ hội hưởng thụ tiện nghi tốt đẹp từ hoàn cảnh (lesser benefic). Đánh giá và tự đánh giá, phân biệt hay dở tốt xấu, giữ thăng bằng hài hoà, tạo dựng hoà khí, gu thẩm mỹ. Đại diện cho phái đẹp, văn nghệ sĩ, cái đẹp.",
    "mars": "Sao Hỏa quản lý hành động, động tác, hoạt động cơ bắp, cách hành xử để giành lấy điều mình muốn, dục vọng chinh phục, hoạt động của năng lượng thể chất (lesser malefic). Làm gì để chống đối, đấu tranh, trấn áp. Cơn giận, cách nổi giận. Đại diện cho phái mạnh, kẻ báo thù, quân đội, vũ khí, thể thao.",
    "jupiter": "Sao Mộc khuếch đại những gì nó chạm vào. Là dấu ấn nghiệp về nơi cá nhân từng được quý nhân nâng đỡ (greater benefic). Cách đặt niềm tin vào thế giới bên ngoài, gắn kết các nguồn lực, thực hiện công tác tuyên truyền. Đại diện cho công lý, tôn giáo, bậc hiền trí, triết gia, người thầy, quý nhân.",
    "saturn": "Sao Thổ là dấu ấn nghiệp về nơi cá nhân từng gặp phải khó khăn lớn nhất, nơi đã phải trả giá xứng đáng (greater malefic). Tạo ra tâm trạng cam chịu, sự chùn bước, nỗi lo sợ, hoặc tính cẩn trọng, khả năng chấp nhận hiện thực khó khăn, tôn trọng các giới hạn. Đại diện cho nhà cầm quyền, pháp luật, người già dặn.",
    "uranus": "Sao Thiên Vương quản lý cảm giác về xã hội. Là dấu ấn nghiệp về cộng đồng nơi 'ta' từng sinh hoạt lâu dài. Tạo ra quan niệm chủ quan về sự bình thường khách quan. Thúc đẩy con người sống lập dị, nổi loạn, khác đời hoặc thích ứng cộng đồng mới. Đại diện cho người hoạt động xã hội, kẻ sống ngoài vòng pháp luật, kẻ lập dị.",
    "neptune": "Sao Hải Vương là dấu ấn nghiệp về trạng thái trước khi sinh ra, nơi cái hữu hạn tiếp xúc cái vô hạn. Hy vọng được trải nghiệm những điều phi thường sinh ra ảo tưởng, xu hướng lý tưởng hoá, thần thánh hoá. Hành vi thoát ly thực tại. Đại diện cho người sống bằng đam mê, người cuồng tín, người mắc nghiện, các vị thánh sống, kẻ mơ mộng.",
    "pluto": "Sao Diêm Vương là dấu hiệu nghiệp về nơi cá nhân từng đối mặt với sự cấm đoán, cảm giác cầu bất đắc, không cam lòng, từng chịu đựng cảm giác thiếu thốn và khao khát. Chỉ ra tâm tham ái, sân hận và khả năng kìm nén khát vọng. Đại diện cho giới xã hội đen, kẻ nắm quyền lực ngầm, kẻ mang thù, phù thuỷ, pháp sư.",
    "north_node": "La Hầu là điểm nghiệp quả, chỉ hướng phát triển của linh hồn trong kiếp này. Đây là nơi bạn cần hướng tới để trưởng thành và hoàn thiện bản thân.",
    "south_node": "Kế Hầu là điểm nghiệp quá khứ, chỉ những thói quen và tài năng đã có từ kiếp trước. Đây là nơi bạn cần buông bỏ để tiến về phía trước.",
    "ascendant": "Cung Mọc đại diện cho cách bạn thể hiện bản thân ra thế giới bên ngoài. Là ấn tượng đầu tiên bạn tạo ra cho người khác, là mặt nạ xã hội và cách tiếp cận cuộc sống.",
    "mc": "Thiên Đỉnh (MC) đại diện cho sự nghiệp, tham vọng và vị thế xã hội. Là đỉnh cao bạn hướng tới trong cuộc đời, cách người khác nhìn nhận bạn ở vị trí công khai.",
    "descendant": "Cung Lặn (DSC) đại diện cho các mối quan hệ đối tác, hôn nhân và cách bạn tương tác với người khác trong các mối quan hệ một-một. Là phẩm chất bạn tìm kiếm ở người bạn đời.",
    "ic": "Thiên Đế (IC) đại diện cho nền tảng cảm xúc, gia đình, cội nguồn và tuổi thơ. Là nơi bạn tìm thấy sự an toàn và cảm giác thuộc về.",
}

SIGN_KEYWORDS_VI: Dict[str, Dict[str, List[str]]] = {
    "aries": {
        "positive": [
            "bộc trực, thẳng thắn", "dứt điểm, bột phát", "độc lập, tự chủ",
            "tiên phong, đầu têu", "hoạt bát, sôi nổi", "trẻ trung, nhiệt huyết",
            "can đảm, liều lĩnh", "tinh thần khởi xướng", "dám nghĩ dám làm",
            "làm lại từ đầu không ngại", "minh bạch, rõ ràng",
        ],
        "negative": [
            "ích kỷ, duy ngã", "nóng nảy, thiếu kiên nhẫn", "hấp tấp, manh động",
            "đầu voi đuôi chuột", "ấu trĩ, ganh đua", "ngang ngược, độc đoán",
            "cậy mạnh, hiếu thắng", "trẻ trâu, tăng động", "tự tung tự tác",
        ],
        "core": [
            "đơn giản, rõ ràng, một là một hai là hai", "tự thân gánh vác, làm một mình",
            "dốc hết tất cả cho một cú duy nhất, xả cạn", "không còn gì để mất",
            "mới mẻ, lần đầu, như lần đầu", "nổi bão, điên máu",
            "trắng trợn, minh bạch", "nhanh nhất, tự do",
        ],
        "short_description": "Bộc trực, thẳng thắn, tiên phong và độc lập. Người có năng lượng Bạch Dương hành động trước, nghĩ sau, luôn sẵn sàng cho những khởi đầu mới.",
        "potential_issues": "Nóng nảy, thiếu kiên nhẫn, hấp tấp, dễ bỏ cuộc giữa chừng, ích kỷ vô tình.",
    },
    "taurus": {
        "positive": [
            "chậm rãi, trầm ổn", "vững chắc, kiên định", "cẩn thận, thực tế",
            "trầm tĩnh, thực dụng", "ổn định, đáng tin cậy", "kiên nhẫn, bền bỉ",
            "trung thành", "có khả năng tập trung cao",
        ],
        "negative": [
            "ương bướng, bảo thủ", "trì trệ, ù lì", "chống thấm, nước đổ lá khoai",
            "hiếu lợi, thực dụng quá mức", "khó thay đổi", "sở hữu cao, chiếm hữu",
            "đồng nát", "ham hưởng thụ vật chất",
        ],
        "core": [
            "khoan thai, từ từ rồi khoai sẽ dừ", "mưa dầm thấm lâu",
            "chất, hữu xạ tự nhiên hương", "biết đủ",
            "phân định rõ cái gì là của ai", "quán tính cao",
            "phán đoán theo ấn tượng đầu tiên", "uống nước cả cặn",
        ],
        "short_description": "Kiên định, thực tế, vững chắc như núi. Người Kim Ngưu xây dựng cuộc sống ổn định và bền vững qua thời gian.",
        "potential_issues": "Bảo thủ, chậm thay đổi, quá coi trọng vật chất, khó thích nghi với cái mới.",
    },
    "gemini": {
        "positive": [
            "tò mò, ham hiểu biết", "lanh lợi, tháo vát", "linh hoạt, tuỳ cơ ứng biến",
            "hoạt bát, nhanh nhẹn", "đa chiều, hiểu nhiều biết rộng",
            "khả năng giao tiếp tốt", "khả năng thích nghi cao",
        ],
        "negative": [
            "hời hợt, thiếu chiều sâu", "hay thay đổi, lật lọng",
            "giảo hoạt, tinh quái", "mồm mép, thị phi",
            "bắt cá hai tay, sống hai mặt", "khó nắm bắt, khó kiểm soát",
            "phân tâm, thiếu tập trung",
        ],
        "core": [
            "tam sao thất bản", "sao chép, mô phỏng, bắt chước",
            "hàng nhái, thế thân", "nguỵ biện, đánh tráo khái niệm",
            "ở bầu thì tròn ở ống thì dài", "quét rộng nhưng không sâu",
            "trông có vẻ giống với",
        ],
        "short_description": "Linh hoạt, tò mò và giao tiếp giỏi. Người Song Tử luôn tìm kiếm thông tin mới và thích nghi nhanh với mọi hoàn cảnh.",
        "potential_issues": "Hời hợt, thiếu kiên định, dễ phân tán năng lượng, khó giữ cam kết lâu dài.",
    },
    "cancer": {
        "positive": [
            "giàu cảm xúc, đồng cảm", "biết chăm sóc, che chở", "trực giác tốt",
            "bao dung, cảm thông", "chung thuỷ, gắn bó", "khả năng cảm hoá",
            "ấm áp, đáng yêu", "trí nhớ cảm xúc tốt",
        ],
        "negative": [
            "đa sầu đa cảm, thất thường", "mong manh dễ vỡ", "rụt rè, nhút nhát",
            "quắp chặt không nhả", "ỷ lại, thiên vị", "sến sẩm, buồn nôn",
            "dễ bị tổn thương", "hay hoài niệm, sống trong quá khứ",
        ],
        "core": [
            "sáng nắng chiều mưa giữa trưa sương mù", "ngoài cứng trong mềm",
            "đau nỗi đau của người khác", "mềm lòng trước kẻ nhỏ yếu",
            "nỗi buồn, nước mắt", "nhớ nhung, hoài niệm",
            "tính gà mẹ", "chó cậy gần nhà gà cậy gần chuồng",
            "lý lẽ của trái tim", "phân biệt thân sơ",
        ],
        "short_description": "Nhạy cảm, giàu cảm xúc và gắn bó gia đình. Người Cự Giải có trực giác mạnh và bản năng chăm sóc người khác.",
        "potential_issues": "Dễ tổn thương, thất thường cảm xúc, quá phụ thuộc vào người thân, khó buông bỏ quá khứ.",
    },
    "leo": {
        "positive": [
            "rạng rỡ, vui tươi", "hào phóng, rộng lượng", "sáng tạo, nghệ thuật",
            "nhiệt tình, đam mê", "hài hước, thú vị", "lạc quan, yêu đời",
            "lãnh đạo tự nhiên", "trung thành, bảo vệ",
        ],
        "negative": [
            "kiêu hãnh, hách dịch", "thích phô trương, chơi nổi", "tự luyến, tự mãn",
            "ưa phỉnh, thích được khen", "kênh kiệu, sang chảnh",
            "thích so sánh hơn kém", "quá coi trọng hình thức",
        ],
        "core": [
            "nụ cười, niềm vui", "oách, oai vệ", "đã cho thì không ghi nợ",
            "dáng vẻ tôn quý, rực rỡ", "lấy bản thân làm trung tâm",
            "không phải cái gì lấp lánh cũng là vàng", "phô trương, đú",
            "đắt giá",
        ],
        "short_description": "Tỏa sáng, hào phóng và tràn đầy sức sống. Người Sư Tử có trái tim ấm áp và khả năng lãnh đạo thiên bẩm.",
        "potential_issues": "Kiêu ngạo, thích kiểm soát, quá coi trọng bản thân, khó chấp nhận thất bại.",
    },
    "virgo": {
        "positive": [
            "tỉ mỉ, cẩn thận", "chính xác, sắc sảo", "khéo léo, tinh xảo",
            "có tiêu chuẩn, biết chừng mực", "chăm chỉ, cần cù",
            "phân tích tốt", "tinh thần phục vụ",
        ],
        "negative": [
            "cầu toàn quá mức", "khắt khe, soi mói", "hay chỉ trích, phê phán",
            "lẩn mẩn, lọ mọ", "khuôn mẫu, cứng nhắc", "dễ lo lắng, căng thẳng",
            "nô tính, ôm việc",
        ],
        "core": [
            "để ý tiểu tiết", "khuôn vàng thước ngọc", "thứ hễ lơ là sẽ suy yếu",
            "lành làm gáo vỡ làm muôi", "phê bình và tự phê bình",
            "sạch sẽ thanh khiết", "tự làm mới thấy hài lòng",
            "không chê vào đâu được",
        ],
        "short_description": "Tỉ mỉ, phân tích và cầu toàn. Người Xử Nữ có tài năng trong công việc đòi hỏi sự chính xác và tinh thần phục vụ cao.",
        "potential_issues": "Cầu toàn quá mức, lo lắng thái quá, khắt khe với bản thân và người khác, khó hài lòng.",
    },
    "libra": {
        "positive": [
            "lịch thiệp, tao nhã", "công bằng, đúng đắn", "khách quan, nhìn hai chiều",
            "hài hoà, cân bằng", "thẩm mỹ tốt", "ngoại giao giỏi",
            "hợp tác, dung hoà",
        ],
        "negative": [
            "do dự, chậm quyết định", "phụ thuộc, thiếu độc lập", "giả tạo, khách sáo",
            "sáo rỗng, bề ngoài", "tránh xung đột", "nước đôi, lập lờ",
            "bánh bèo, yếu đuối",
        ],
        "core": [
            "đắn đo, cân nhắc", "chông chênh và giữ thăng bằng",
            "cả nể, nhún nhường", "vôi ve bề ngoài",
            "tô vẽ, hàng giả", "nửa nạc nửa mỡ",
            "xã giao, đong đưa",
        ],
        "short_description": "Cân bằng, ngoại giao và thẩm mỹ. Người Thiên Bình khéo léo trong giao tiếp, có khiếu thẩm mỹ và tìm kiếm sự hài hòa.",
        "potential_issues": "Do dự, thiếu quyết đoán, phụ thuộc vào người khác, tránh xung đột bằng mọi giá.",
    },
    "scorpio": {
        "positive": [
            "sâu sắc, thấu suốt", "mãnh liệt, đam mê", "kiên định, ý chí sắt đá",
            "khả năng chuyển hóa", "bí ẩn, hấp dẫn", "trung thành tuyệt đối",
            "nhìn thấu bản chất", "quyết liệt, dứt khoát",
        ],
        "negative": [
            "nghi hoặc, đa nghi", "khao khát, cực đoan", "thao túng, kiểm soát",
            "ghen tuông, đố kị", "ôm hận, ghi thù", "bất an, bất ổn",
            "ám ảnh, cố chấp", "bí mật, nửa kín nửa hở",
        ],
        "core": [
            "không trọn vẹn, thiếu hụt", "nắm giữ tất cả trong lòng bàn tay",
            "xỏ mũi và bị xỏ mũi", "nhọ, nhẫn, nhục",
            "tảng băng trôi", "cái chết và sự tái sinh",
            "chết không nhắm mắt", "vô giá hoặc vô giá trị",
        ],
        "short_description": "Mãnh liệt, sâu sắc và bí ẩn. Người Bọ Cạp có ý chí sắt đá, khả năng chuyển hóa phi thường và nhìn thấu bản chất mọi việc.",
        "potential_issues": "Ghen tuông, kiểm soát, thao túng, khó tha thứ, dễ bị ám ảnh bởi quá khứ.",
    },
    "sagittarius": {
        "positive": [
            "tập trung, chuyên tâm", "cởi mở, hào phóng", "lạc quan, tin tưởng",
            "thẳng thắn, trung thành", "có phương hướng, có mục tiêu",
            "khả năng định hướng tốt", "tinh thần khám phá, phiêu lưu",
            "truyền cảm hứng",
        ],
        "negative": [
            "tự cho mình là đúng", "phiến diện, một chiều", "vô trách nhiệm",
            "hoang phí", "được đằng chân lân đằng đầu",
            "cạn tàu ráo máng", "bỏ đá xuống giếng",
            "cuồng tín, tẩy não",
        ],
        "core": [
            "tuyên truyền, lôi kéo, lan truyền", "đâm lao phải theo lao",
            "làm gì là làm đến cùng", "luôn tiến về phía trước",
            "lạc quan tếu, phởn", "tin vào tương lai, có tiền đồ",
            "thầy đời", "tính quân tử",
        ],
        "short_description": "Lạc quan, cởi mở và yêu tự do. Người Nhân Mã luôn tìm kiếm chân lý và mở rộng chân trời tri thức.",
        "potential_issues": "Thiếu tế nhị, vô trách nhiệm, cuồng tín, khó ở yên một chỗ.",
    },
    "capricorn": {
        "positive": [
            "thận trọng, tỉnh táo", "kỷ luật, quy củ", "kiên trì, bền bỉ",
            "có tổ chức, bao quát", "dám làm dám chịu", "tôn trọng kinh nghiệm",
            "có trách nhiệm", "biết chừng mực",
        ],
        "negative": [
            "khô khan, lạnh lùng", "bảo thủ, cứng nhắc", "thiếu cảm thông",
            "khắc nghiệt, khắc kỷ", "tự ti, mặc cảm", "hay bàn lùi",
            "quá coi trọng địa vị", "lo xa thái quá",
        ],
        "core": [
            "nhân quả, gieo gì gặt nấy", "cái đầu lạnh",
            "trọng kỷ luật, tôn trọng chuyên gia", "lão luyện, lịch duyệt",
            "có bố cục, có kết cấu", "ý thức về tính hữu hạn",
            "thời gian của quá khứ, lịch sử", "hàn lâm, kinh điển",
        ],
        "short_description": "Kỷ luật, tham vọng và kiên trì. Người Ma Kết xây dựng thành công từng bước một bằng nỗ lực không ngừng.",
        "potential_issues": "Quá coi trọng công việc, lạnh lùng cảm xúc, bảo thủ, khó thư giãn.",
    },
    "aquarius": {
        "positive": [
            "độc đáo, sáng tạo", "cởi mở, tiến bộ", "tư duy tương lai",
            "nhân đạo, vị tha", "khách quan, không đánh giá", "bản sắc riêng",
            "tinh thần tự do", "khả năng dự báo",
        ],
        "negative": [
            "lập dị, khác người", "phá rào, vô kỷ luật", "dửng dưng, vô tình",
            "a dua, theo đuôi", "nhàm chán, dễ chán", "cà lơ phất phơ",
            "dám làm không dám chịu", "trống đánh xuôi kèn thổi ngược",
        ],
        "core": [
            "phân biệt trên cơ sở giống và khác", "chấp nhận mọi thứ như nó vốn có",
            "muốn tung hê hiện trạng", "giật gân, gây sốc",
            "sự công cộng hoá", "phá cách, không chịu ràng buộc",
            "thiên tài hoặc chầu rìa", "hàng kém chất lượng vs hàng độc",
        ],
        "short_description": "Độc đáo, tiến bộ và yêu tự do. Người Bảo Bình có tư duy khác biệt và luôn hướng về tương lai.",
        "potential_issues": "Lập dị, xa cách cảm xúc, khó gần gũi, nổi loạn vô cớ.",
    },
    "pisces": {
        "positive": [
            "giàu trí tưởng tượng", "sáng tạo, nghệ thuật", "đồng cảm sâu sắc",
            "trực giác tâm linh", "vị tha, bao dung", "linh hoạt, dễ thích nghi",
            "khả năng thư giãn", "biết tha thứ",
        ],
        "negative": [
            "mơ hồ, không rõ ràng", "thiếu thực tế", "dễ bị lây nhiễm cảm xúc",
            "ảo tưởng, tự lừa dối", "vô tổ chức, hỗn độn", "thiếu nguyên tắc",
            "nghiện ngập, thoát ly", "tuyệt vọng, tự huỷ",
        ],
        "core": [
            "mơ mộng viển vông", "tâm hồn treo ngược cành cây",
            "quên lãng", "ảo giác, hư cấu",
            "chỉ thấy thứ muốn thấy", "trên mây, cần hạ cánh gấp",
            "xoã, bùng, phủi", "giả ngu, giả khờ",
            "biết chết liền",
        ],
        "short_description": "Nhạy cảm, mơ mộng và giàu lòng trắc ẩn. Người Song Ngư có trí tưởng tượng phong phú và khả năng thấu hiểu sâu sắc.",
        "potential_issues": "Ảo tưởng, thiếu thực tế, dễ bị lợi dụng, khó đối mặt với hiện thực khắc nghiệt.",
    },
}

HOUSE_KEYWORDS_VI: Dict[int, Dict[str, List[str]]] = {
    1: {
        "title": "Bản Thân (Nhà 1)",
        "keywords": [
            "tự hình dung về mình", "thể diện, mặt mũi", "thái độ không thương lượng",
            "ấn tượng ban đầu", "cách bắt đầu mọi chuyện", "khuynh hướng không đụng hàng",
            "nơi tìm ưu điểm của ta, nhược điểm của người khác", "thái độ khi thắng thế",
            "cách nâng cao quan điểm", "nhìn cái mặt là thấy...", "ấn tượng tổng quát",
            "điều kiện tồn tại", "không thể đỡ được", "cố tình gây sự",
            "cách phát huy ưu điểm thế mạnh",
        ],
        "description": "Là nhà của cái tôi, cách người khác nhìn nhận về bạn. Đây là nơi bạn tạo ấn tượng đầu tiên và thể hiện bản sắc cá nhân.",
    },
    2: {
        "title": "Tài Chính (Nhà 2)",
        "keywords": [
            "tự đánh giá bản thân", "cách xử trí quyền sở hữu", "quyền lợi của ta",
            "thu nhập do lao động", "quản lý tài chính", "cách ăn uống tiêu xài",
            "cảm giác về những gì mình có", "khả năng khai thác bồi dưỡng",
            "thứ có thể mài ra ăn được", "chuyện có lợi mới làm",
            "thứ có giá trị", "trí nhớ, ký ức, quá khứ",
            "vốn liếng", "khả năng đồng hoá",
        ],
        "description": "Là nhà của tài sản và giá trị bản thân. Nơi bạn xây dựng sự an toàn vật chất và lòng tự trọng.",
    },
    3: {
        "title": "Giao Tiếp (Nhà 3)",
        "keywords": [
            "học hỏi trực quan", "ngôn ngữ và giao tiếp", "thư tín công vụ",
            "nghe nói đọc viết", "anh chị em ruột", "quan hệ sơ giao",
            "môi trường sinh hoạt hàng ngày", "láng giềng", "trường học",
            "các chuyến đi ngắn", "chuyện nhỏ", "mắt thấy tai nghe",
            "cách đặt danh pháp tên gọi", "kết tinh trí tuệ",
            "cách diễn đạt truyền đạt", "cứ mở mồm ra là...",
        ],
        "description": "Là nhà của giao tiếp và học hỏi. Nơi bạn kết nối với môi trường xung quanh qua ngôn ngữ và tri thức.",
    },
    4: {
        "title": "Gia Đình (Nhà 4)",
        "keywords": [
            "cách lấy lại thăng bằng tâm lý", "thói quen", "phản xạ có điều kiện",
            "vẫn thế không có gì thay đổi (gây hoài niệm)", "mái ấm, cha mẹ",
            "nơi cho sự khích lệ ủng hộ", "cảm giác gắn bó duyên phận",
            "con cái - đối tượng cần săn sóc", "sự cưu mang",
            "cách săn sóc quan tâm", "cách phục hồi sức sống, sạc pin",
            "quê hương gốc rễ", "chuyện vặt vãnh", "niềm tin vào thế giới",
        ],
        "description": "Là nhà của cội nguồn và gia đình. Nơi bạn tìm thấy sự an toàn cảm xúc và nạp lại năng lượng.",
    },
    5: {
        "title": "Sáng Tạo (Nhà 5)",
        "keywords": [
            "sự tự thể hiện", "đối tượng đáng khoe khoang", "thú vui giải trí đồ chơi",
            "hoạt động sáng tạo", "đứa con tinh thần", "con cái - niềm tự hào",
            "sự lãng mạn hẹn hò", "cách tán tỉnh cưa cẩm", "niềm vui",
            "điều kiện để tiếp nhận kích thích", "đối tượng đặc quyền đặc lợi",
            "thái độ với người đặc biệt", "bóng đèn (cướp hào quang)",
            "đắt giá", "trò vui",
        ],
        "description": "Là nhà của sáng tạo và niềm vui. Nơi bạn thể hiện bản thân, yêu đương và tận hưởng cuộc sống.",
    },
    6: {
        "title": "Công Việc (Nhà 6)",
        "keywords": [
            "công việc và trách nhiệm thường nhật", "áp lực cuộc sống",
            "dòng đời xô đẩy", "cách gây căng thẳng", "bị bắt chẹt và cách bắt chẹt",
            "khả năng đoán biết nhu cầu người khác", "tiêu chuẩn con nhà lành",
            "rèn luyện kỹ năng", "học hỏi thể hiện kỹ năng",
            "thứ hễ lơ là sẽ suy yếu", "công ăn việc làm", "thái độ người làm công",
            "sức khoẻ", "phục vụ người khác", "thú cưng",
            "chuyện bất đắc dĩ bất khả kháng", "khả năng nhìn thấy việc cần làm",
        ],
        "description": "Là nhà của công việc và sức khỏe. Nơi bạn đối mặt với trách nhiệm hàng ngày và rèn luyện kỹ năng.",
    },
    7: {
        "title": "Hôn Nhân (Nhà 7)",
        "keywords": [
            "hôn nhân bạn đời", "đối tác làm ăn", "quan hệ cần nỗ lực duy trì",
            "cách xưng hô phân vai vế", "điều kiện duy trì quan hệ lâu dài",
            "thoả thuận hợp đồng", "xã giao cần công sức", "đối thủ công khai",
            "nơi tìm ưu điểm người khác và khuyết điểm mình", "thế yếu không nắm đằng chuôi",
            "nhượng bộ thoả hiệp", "cảm thấy cần người khác hơn", "lệ thuộc",
        ],
        "description": "Là nhà của các mối quan hệ đối tác. Nơi bạn học cách hợp tác, thoả hiệp và xây dựng cam kết lâu dài.",
    },
    8: {
        "title": "Chuyển Hóa (Nhà 8)",
        "keywords": [
            "xử lý tài nguyên người khác", "tổn hại lợi ích người khác",
            "nợ và vay nợ", "đầu tư", "chia sẻ quyền và trách nhiệm tài chính",
            "chõ mũi vào chuyện người khác", "cái ta muốn có của người khác",
            "chiêu trò mưu đồ", "cảm giác mất mặt", "thái độ mặt dày",
            "sinh hoạt tình dục", "quan hệ quyền lợi chung",
            "miếng ghép bị thiếu của nhân cách", "thay đổi bản thân",
            "cái chết và tái sinh", "chết không nhắm mắt",
            "cấm đoán xã hội", "vô giá hoặc vô giá trị",
        ],
        "description": "Là nhà của chuyển hóa và tái sinh. Nơi bạn đối mặt với những khía cạnh sâu kín nhất của cuộc sống.",
    },
    9: {
        "title": "Triết Lý (Nhà 9)",
        "keywords": [
            "kết tinh trí tuệ của người khác", "cái đáng học hỏi",
            "tranh thủ nguồn lực bên ngoài", "học hỏi từ trí tuệ người khác",
            "người thầy người đưa đường chỉ lối", "quý nhân nâng đỡ",
            "con đường nâng cao chính mình", "tôn giáo đức tin",
            "công lý và luân lý", "chân lý, đạo lý",
            "trông cậy tin tưởng", "làm bằng niềm tin",
            "chuyến đi xa du học", "vận may thăng tiến",
            "chuyện lớn",
        ],
        "description": "Là nhà của triết lý và khám phá. Nơi bạn tìm kiếm ý nghĩa cuộc sống qua học hỏi và trải nghiệm.",
    },
    10: {
        "title": "Sự Nghiệp (Nhà 10)",
        "keywords": [
            "nơi cần bỏ nỗ lực lớn nhất", "hoạt động nghiêm túc",
            "tạo dựng sự nghiệp uy tín địa vị", "thẩm quyền",
            "quan hệ với cấp trên", "hình ảnh khi làm sếp",
            "nơi không thể ở lâu", "dễ gây mệt mỏi thấy phiền",
            "người ta kính sợ hoặc ghê tởm", "thể hiện uy thế ra oai",
            "chuyện doạ người", "thứ đáng sợ",
            "ca này khó", "chuyện có độ khó cao",
        ],
        "description": "Là nhà của sự nghiệp và danh vọng. Nơi bạn khẳng định vị thế xã hội và gặt hái thành quả từ nỗ lực.",
    },
    11: {
        "title": "Bạn Bè (Nhà 11)",
        "keywords": [
            "mục tiêu đích đến trong đời", "chí hướng đồng chí",
            "theo đuổi mục tiêu lâu dài", "khả năng lập và tuân thủ kế hoạch",
            "thế lực lợi ích nhóm", "quan hệ hợp tác bậc cao", "sự nhàn hạ",
            "bạn và bè sinh hoạt hội nhóm", "gọi thì đến đuổi thì đi", "sự hoà đồng",
            "chuyện rảnh ruồi thừa hơi", "chuyện nhạt nhẽo",
            "chỉ làm khi có thời gian dư thừa", "thứ rẻ tiền vs vô giá",
            "sống không phải để nhận đánh giá",
        ],
        "description": "Là nhà của bạn bè và lý tưởng. Nơi bạn kết nối với cộng đồng và theo đuổi những mục tiêu dài hạn.",
    },
    12: {
        "title": "Tiềm Thức (Nhà 12)",
        "keywords": [
            "bỏ mặc thực tại", "ngông (bất chấp)", "điên (mất kết nối)",
            "thư giãn thoải mái", "làm người khác thư giãn",
            "thói tật vô ý thức", "ước gì đây không phải sự thật",
            "phải giết ngay không để kịp đẻ trứng",
            "kẻ thù giấu mặt", "bị đâm sau lưng",
            "thế giới nội tâm tiềm thức", "cách giấu diếm che đậy",
            "bí mật không ai biết", "nơi lẩn trốn hiện thực",
            "thứ bị quên lãng", "chấm dứt hoàn toàn",
            "tìm cái lỗ để chui xuống", "chết cũng cam lòng",
            "tự huỷ hoại", "tuyệt vọng", "chuyện đã qua không thể vãn hồi",
        ],
        "description": "Là nhà của tiềm thức và tâm linh. Nơi bạn đối mặt với những điều ẩn giấu sâu thẳm trong tâm hồn.",
    },
}

SIGN_NATURAL_RULER: Dict[str, str] = {
    "aries": "mars", "taurus": "venus", "gemini": "mercury",
    "cancer": "moon", "leo": "sun", "virgo": "mercury",
    "libra": "venus", "scorpio": "pluto", "sagittarius": "jupiter",
    "capricorn": "saturn", "aquarius": "uranus", "pisces": "neptune",
}

HOUSE_NATURAL_RULER: Dict[int, str] = {
    1: "mars", 2: "venus", 3: "mercury", 4: "moon", 5: "sun",
    6: "mercury", 7: "venus", 8: "pluto", 9: "jupiter",
    10: "saturn", 11: "uranus", 12: "neptune",
}

SIGN_NAME_VI: Dict[str, str] = {
    "aries": "Bạch Dương", "taurus": "Kim Ngưu", "gemini": "Song Tử",
    "cancer": "Cự Giải", "leo": "Sư Tử", "virgo": "Xử Nữ",
    "libra": "Thiên Bình", "scorpio": "Bọ Cạp", "sagittarius": "Nhân Mã",
    "capricorn": "Ma Kết", "aquarius": "Bảo Bình", "pisces": "Song Ngư",
}

HOUSE_NAME_VI: Dict[int, str] = {
    1: "Nhà 1 (Bản Thân)", 2: "Nhà 2 (Tài Chính)", 3: "Nhà 3 (Giao Tiếp)",
    4: "Nhà 4 (Gia Đình)", 5: "Nhà 5 (Sáng Tạo)", 6: "Nhà 6 (Công Việc)",
    7: "Nhà 7 (Hôn Nhân)", 8: "Nhà 8 (Chuyển Hóa)", 9: "Nhà 9 (Triết Lý)",
    10: "Nhà 10 (Sự Nghiệp)", 11: "Nhà 11 (Bạn Bè)", 12: "Nhà 12 (Tiềm Thức)",
}

SIGN_ELEMENT_VI: Dict[str, str] = {
    "aries": "lửa", "taurus": "đất", "gemini": "khí", "cancer": "nước",
    "leo": "lửa", "virgo": "đất", "libra": "khí", "scorpio": "nước",
    "sagittarius": "lửa", "capricorn": "đất", "aquarius": "khí", "pisces": "nước",
}

SIGN_QUALITY_VI: Dict[str, str] = {
    "aries": "thống lĩnh", "taurus": "cố định", "gemini": "biến đổi",
    "cancer": "thống lĩnh", "leo": "cố định", "virgo": "biến đổi",
    "libra": "thống lĩnh", "scorpio": "cố định", "sagittarius": "biến đổi",
    "capricorn": "thống lĩnh", "aquarius": "cố định", "pisces": "biến đổi",
}


def get_sign_keywords(sign: str) -> Dict[str, List[str]]:
    return SIGN_KEYWORDS_VI.get(sign, {})


def get_house_keywords(house: int) -> Dict[str, List[str]]:
    return HOUSE_KEYWORDS_VI.get(house, {})


def get_sign_description(sign: str) -> str:
    data = SIGN_KEYWORDS_VI.get(sign)
    if not data:
        return ""
    pos = "; ".join(data.get("positive", [])[:5])
    neg = "; ".join(data.get("negative", [])[:4])
    return f"Tích cực: {pos}. Thách thức: {neg}."


def get_sign_short_description(sign: str) -> str:
    data = SIGN_KEYWORDS_VI.get(sign)
    return data.get("short_description", "") if data else ""


def get_sign_potential_issues(sign: str) -> str:
    data = SIGN_KEYWORDS_VI.get(sign)
    return data.get("potential_issues", "") if data else ""


def get_house_description(house: int) -> str:
    data = HOUSE_KEYWORDS_VI.get(house)
    return data.get("description", "") if data else ""


def get_house_title(house: int) -> str:
    data = HOUSE_KEYWORDS_VI.get(house)
    return data.get("title", f"Nhà {house}") if data else f"Nhà {house}"


def get_planet_function(planet: str) -> str:
    return PLANET_FUNCTIONS_VI.get(planet, "")
