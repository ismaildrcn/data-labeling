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
        

        M100 = "Çalışma başarıyla oluşturuldu, etiketlemeye başlayabilirsiniz."

    class Warning(BaseEnum):
        @property
        def icon(self):
            return ":/images/templates/images/warning.svg"

        @property
        def type(self):
            return "Uyarı"
        

        M200 = "Henüz hiç etiketleme yapmadınız."
    
    class Error(BaseEnum):
        @property
        def icon(self):
            return ":/images/templates/images/error.svg"

        @property
        def type(self):
            return "Hata"
        

        M300 = "Lütfen devam etmeden önce etiket oluşturmayı veya etiketlerinizi içe aktarmayı deneyin!"

    class Action(BaseEnum):
        @property
        def icon(self):
            return ":/images/templates/images/fire.svg"

        @property
        def type(self):
            return "Seç"
        

        M400 = "Etiket türü atanmamış seçimleriniz mevcut. Eğer devam ederseniz sadece atanmış etiketler dışarıya aktarılacaktır. Onaylıyor musunuz?"