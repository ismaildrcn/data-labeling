from enum import Enum


class BaseEnum(Enum):
    @property
    def message(self):
        return self.value
    
    @property
    def code(self):
        return self.name[1:]



class PopupMessages(object):
    
    class Info(BaseEnum):
        @property
        def icon(self):
            return ":/images/templates/images/info.svg"

        @property
        def type(self):
            return "Bilgi"
        

        M100 = "Çalışmanız başarıyla oluşturuldu, etiketlemeye başlayabilirsiniz."
        M101 = "Çalışmanız başarıyla seçmiş olduğunuz dizine aktarılmıştır."

    class Warning(BaseEnum):
        @property
        def icon(self):
            return ":/images/templates/images/warning.svg"

        @property
        def type(self):
            return "Uyarı"
        

        M200 = "Henüz hiç etiketleme yapmadınız."
        M201 = "Bilgisayara aktarılacak etiket bulunamadı."
        M202 = "Bu isimlendirmeye ait zaten bir etiketiniz var, lütfen farklı bir isim girmeyi deneyiniz."
        M203 = "Bazı görseller aktarmış olduğunuz dizinde bulunamadı (görsellerin yeri değişmiş olabilir), bu görseller ve etiketleri dışarıya aktarılmayacaktır."
        M204 = "Böyle bir kullanıcı bulunamadı. Lütfen kullanıcı adınızı doğru girdiğinizden emin olun!"
    
    class Error(BaseEnum):
        @property
        def icon(self):
            return ":/images/templates/images/error.svg"

        @property
        def type(self):
            return "Hata"
        

        M300 = "Lütfen devam etmeden önce etiket oluşturmayı veya etiketlerinizi içe aktarmayı deneyin!"
        M301 = "Çalışmanız bilgisayara kaydedilirken bir hata oluştu, lütfen yetkili ile paylaşınız."
        M302 = "Seçmiş olduğunuz dosya bu uygulama ile uyumlu değil, lütfen uygulamayı kullanarak dışarıya çıkarttığınız dosyaları kullanmayı deneyiniz."

    class Action(BaseEnum):
        @property
        def icon(self):
            return ":/images/templates/images/fire.svg"

        @property
        def type(self):
            return "Seç"
        

        M400 = "Etiket türü atanmamış seçimleriniz mevcut. Eğer devam ederseniz sadece atanmış seçimler bilgisayara aktarılacaktır. Onaylıyor musunuz?"
        M401 = "Etiketleriniz uygulamaya aktarılmak üzere, eğer daha önceden oluşturulmuş etiketleriniz varsa bunlar kaldırılacaktır. Onaylıyor musunuz?"
        M402 = "Çalışmadan ayrılmak istediğinize emin misiniz? Tüm ilerlemenizi kalıcı olarak kaybedeceksiniz."
        M403 = "Etiket tür listesi temizlenecek, devam etmek istiyor musunuz?"
        M404 = "Daha önce yarım bırakılmış bir çalışmanız tespit edildi. Onunla devam etmek ister misiniz?"
        M405 = "Seçmiş olduğunuz görseli silmek üzeresiniz, devam etmek istiyor musunuz?"
        M406 = "Silmek istediğiniz görsel üzerinde oluşturulmuş etiketlemeler var. Bunlar kalıcı olarak silinecektir, devam etmek istiyor musunuz?"
    
    class Verify(BaseEnum):
        @property
        def icon(self):
            return ":/images/templates/images/verify.svg"
        
        @property
        def type(self):
            return "Doğrulama"
        
        M500 = "Dikkat kayıtlar kalıcı olarak silinecek, devam etmek için &param kodunu girerek işlemi onaylayınız. İptal etmeniz durumunda uygulama kapatılacaktır."
        M501 = "Dikkat kayıtlar kalıcı olarak silinecek, devam etmek için &param kodunu girerek işlemi onaylayınız."