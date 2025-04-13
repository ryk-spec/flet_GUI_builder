import flet as ft
from enum import Enum
from abc import ABC, abstractmethod
import re
from datetime import datetime
from functools import partial
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64


class ValidateType(Enum):
    on_change = "on_change"
    on_submit = "on_submit"
    on_blur = "on_blur"

class ValidationField(ft.TextField, ABC):
    
    def __init__(self, label: str, validation_type: Enum, **kwargs):
        super().__init__(label=label, **kwargs)
        self.validation_type = validation_type
        self.value = ""
        
    @abstractmethod
    def validate(self, value: str) -> bool:
        pass

class DateField(ValidationField):
    def __init__(self, label: str, validation_type: ValidateType, **kwargs):
        if not isinstance(validation_type, ValidateType):
            raise ValueError("validation_type must be an instance of ValidateType enum")
        super().__init__(label=label, validation_type=validation_type, **kwargs)
        if validation_type == ValidateType.on_change:
            self.on_change = partial(self.validate, value=self.value)
        elif validation_type == ValidateType.on_submit:
            self.on_submit = partial(self.validate, value=self.value)
        elif validation_type == ValidateType.on_blur:
            self.on_blur = partial(self.validate, value=self.value)
        

    def validate(self, e,value: str) -> bool:
        try:
            # Attempt to parse the date string
            match_date = re.match(r"^\d{6}$", self.value)
            if not match_date:
                raise ValueError("Date must be in YYYYMMDD format")
            if match_date:
                year = int(self.value[:2])
                month = int(self.value[2:4])
                day = int(self.value[4:])
                datetime.strptime(f"20{year}-{month}-{day}", "%Y-%m-%d")
                self.error_text = ""
                self.update()
            return True
        except ValueError as error:
            self.error_text = error.args[0]
            self.update()
            return False
        

if __name__ == "__main__":
    
    class MyApp:
        def __init__(self,page:ft.Page):
            self.start_date_field = DateField(
                label="6桁の数字で日付を入力（開始）", 
                validation_type=ValidateType.on_blur,
                width=200)
            self.end_date_field = DateField(
                label="6桁の数字で日付を入力（終了）", 
                validation_type=ValidateType.on_blur,
                width=200)

            self.search_button = ft.ElevatedButton(text="検索",on_click=self.__search_file)

            self.output_text = ft.Text()

            self.date_row = ft.Row(controls=[self.start_date_field, self.end_date_field, self.search_button], alignment=ft.MainAxisAlignment.START)

            self.lot_dropdown = ft.Dropdown(label="lot", width=200,on_change=self._display_fig)
            self.image = ft.Image(width=300, height=300)
            self.data = ft.Container(
                content=ft.TextField(
                    label="実験データ",
                    multiline=True,
                    text_align=ft.TextAlign.LEFT
                ),
                width=500,
                height=300
            )

            self.save_button = ft.ElevatedButton(text="保存")
            page.add(self.date_row)
            page.add(self.output_text)
            page.add(self.lot_dropdown)
            page.add(ft.Row([self.image,self.data],height=300))
            page.add(self.save_button)
            page.title = "Validated TextField Example"
            self.page = page
            
        def __search_file(self,e):
            
            # Perform search logic here
            self.output_text.value = f"日時をqueryとした検索を実行...\n{self.start_date_field.value} - {self.end_date_field.value}"
            self.output_text.update()
            self.lot_dropdown.options = [
                ft.dropdown.Option("lot1"),
                ft.dropdown.Option("lot2"),
                ft.dropdown.Option("lot3"),
            ]
            self.page.update()
        
        def _display_fig(self, e):

            # ダミーデータで画像作成
            X = np.linspace(0, 10, 100)
            y = np.exp(-X**2) + np.random.normal(0, 0.2, 100)
            fig, ax = plt.subplots()
            ax.scatter(x=X,y=y)
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            plt.close(fig)
            buf.seek(0)
            img_bytes = buf.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            self.image.src_base64 = f"{img_b64}"
            # 作成した画像をFletのImageウィジェットで表示
            self.output_text.value = "描画した画像を表示しました"
            self.data.content.value = np.stack([X,y],axis=1)
            self.image.update()
            self.page.update()
            
            
            
    ft.app(target=MyApp)