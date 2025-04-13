import flet as ft
# UserControl と ABC の継承を削除
from datetime import datetime
from enum import Enum # Enum をインポート

# バリデーションイベントの種類を定義するEnum
class ValidationEvent(Enum):
    ON_BLUR = "on_blur"
    ON_CHANGE = "on_change"

# 抽象クラスではなく通常のクラスにする (必要であれば ABC は後で追加可能)
class ValidatedTextField:
    """
    入力値のバリデーション機能を持つTextFieldを管理するクラス (UserControlではない)
    """
    def __init__(self, label: str = "", hint_text: str = "", initial_value: str | None = None, validation_event: ValidationEvent = ValidationEvent.ON_BLUR, on_update=None): # 型ヒントとデフォルト値を変更
        """
        Args:
            label (str): TextFieldのラベル.
            hint_text (str): TextFieldのヒントテキスト.
            initial_value (str | None): TextFieldの初期値.
            validation_event (ValidationEvent): バリデーションを実行するイベント.
            on_update (callable | None): TextFieldの更新が必要な場合に呼び出すコールバック関数 (例: page.update).
        """
        # super().__init__() # UserControlではないので不要
        self.label = label
        self.hint_text = hint_text
        self._initial_value_str = initial_value if initial_value is not None else ""
        self._validation_event = validation_event
        self._is_valid = False # 現在の値が有効かどうかを示すフラグ
        self._on_update = on_update # 更新用コールバック

        # 内部で TextField インスタンスを保持
        self.text_field = ft.TextField(
            label=self.label,
            hint_text=self.hint_text,
            value=self._initial_value_str,
            # バリデーションイベントハンドラをEnumで設定
            on_blur=self._handle_validation if validation_event == ValidationEvent.ON_BLUR else None,
            on_change=self._handle_validation if validation_event == ValidationEvent.ON_CHANGE else None,
        )
        # 初期値に対するバリデーションとエラー表示
        self._validate_value(self._initial_value_str) # _is_valid を設定
        self.text_field.error_text = self._get_error_message(self._initial_value_str) if not self._is_valid else None

    # build メソッドの代わりに、コントロールを取得するメソッドを用意
    def get_control(self) -> ft.TextField:
        """このクラスが管理する ft.TextField コントロールを返す"""
        return self.text_field

    def _handle_validation(self, e: ft.ControlEvent):
        """イベント発生時にバリデーションを実行し、表示を更新する"""
        value = e.control.value
        self._validate_value(value) # _is_valid を更新
        new_error_text = self._get_error_message(value) if not self._is_valid else None
        # エラーテキストが実際に変更された場合のみ更新を試みる
        if self.text_field.error_text != new_error_text:
            self.text_field.error_text = new_error_text
            if self._on_update:
                self._on_update() # 親コンテナに更新を依頼

    # 抽象メソッドではなく、具象メソッドとして実装するか、サブクラスでオーバーライドを強制しない
    def _validate_value(self, value: str) -> bool:
        """
        入力値をバリデーションするメソッド (基底クラスでは常に True).
        サブクラスでオーバーライドして使用する.
        バリデーションが成功した場合は True を、失敗した場合は False を返すように実装する.
        このメソッド内で self._is_valid フラグを更新すること.
        """
        self._is_valid = True # デフォルトは常に有効
        # print(f"Base _validate_value called for '{value}', setting is_valid={self._is_valid}") # デバッグ用
        return True

    def _get_error_message(self, value: str) -> str | None:
        """
        バリデーション失敗時のエラーメッセージを返すメソッド (基底クラスでは常に None).
        サブクラスでオーバーライドして使用する.
        値が有効な場合やエラーメッセージがない場合は None を返す.
        """
        # print(f"Base _get_error_message called for '{value}'") # デバッグ用
        return None # デフォルトはエラーメッセージなし

    @property
    def value(self) -> str:
        """現在のテキストフィールドの文字列を返すプロパティ"""
        return self.text_field.value

    @property
    def is_valid(self) -> bool:
        """現在の入力値が有効かどうかを返すプロパティ"""
        # print(f"Property is_valid returning: {self._is_valid}") # デバッグ用
        return self._is_valid


class DateTimeTextField(ValidatedTextField):
    """
    YYYY-MM-DD HH:MM:SS 形式の日時入力とバリデーションを行うTextFieldを管理するクラス
    """
    def __init__(self, label: str = "日時", hint_text: str = "YYYY-MM-DD", initial_value: str | None = None, validation_event: str = "on_blur", on_update=None):
        self._format = "%Y-%m-%d"
        self._datetime_value: datetime | None = None
        # 基底クラスのコンストラクタを呼び出す
        super().__init__(label=label, hint_text=hint_text, initial_value=initial_value, validation_event=validation_event, on_update=on_update)

    # 基底クラスのメソッドをオーバーライド
    def _validate_value(self, value: str) -> bool:
        """日時形式をバリデーションする"""
        # print(f"DateTime _validate_value called for '{value}'") # デバッグ用
        if not value: # 空の場合は有効とする（必要に応じて変更）
            self._is_valid = False
            self._datetime_value = None
            return False
        try:
            self._datetime_value = datetime.strptime(value, self._format)
            self._is_valid = True
            return True
        except ValueError:
            self._datetime_value = None
            self._is_valid = False
            return False

    # 基底クラスのメソッドをオーバーライド
    def _get_error_message(self, value: str) -> str | None:
        """日時形式エラー時のメッセージを返す"""
        # print(f"DateTime _get_error_message called for '{value}', is_valid={self._is_valid}") # デバッグ用
        if not self._is_valid and value: # 不正かつ空でない場合
             error_msg = f"正しい形式 ({self.hint_text}) で入力してください"
             # print(f"  -> Returning error: {error_msg}") # デバッグ用
             return error_msg
        # print("  -> Returning None (no error)") # デバッグ用
        return None # 有効な場合や空の場合はエラーメッセージなし

    @property
    def datetime_value(self) -> datetime | None:
        """バリデーション済みの日時オブジェクトを返すプロパティ"""
        # print(f"Property datetime_value returning: {self._datetime_value if self.is_valid else None}") # デバッグ用
        return self._datetime_value if self.is_valid else None


# --- 使用例 (テスト用) ---
if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "ValidatedTextField Example (No UserControl)"
        page.vertical_alignment = ft.MainAxisAlignment.START

        # クラスのインスタンスを作成
        # on_update に page.update を渡して、エラー表示が更新されるようにする
        datetime_input = DateTimeTextField(label="開始日時", on_update=page.update)
        datetime_input_initial = DateTimeTextField(label="終了日時", initial_value="2024-12-31", on_update=page.update)
        datetime_input_invalid_initial = DateTimeTextField(label="不正な初期値", initial_value="invalid-date", on_update=page.update)
        datetime_input_onchange = DateTimeTextField(label="入力中に検証", validation_event="on_blur", on_update=page.update)


        def show_value(e):
            print("-" * 20)
            print(f"開始日時: '{datetime_input.value}' / Valid: {datetime_input.is_valid} / Datetime: {datetime_input.datetime_value}")
            print(f"終了日時: '{datetime_input_initial.value}' / Valid: {datetime_input_initial.is_valid} / Datetime: {datetime_input_initial.datetime_value}")
            print(f"不正初期値: '{datetime_input_invalid_initial.value}' / Valid: {datetime_input_invalid_initial.is_valid} / Datetime: {datetime_input_invalid_initial.datetime_value}")
            print(f"入力中検証: '{datetime_input_onchange.value}' / Valid: {datetime_input_onchange.is_valid} / Datetime: {datetime_input_onchange.datetime_value}")


        # ページに追加する際は、クラスインスタンスではなく、get_control() で TextField を取得する
        page.add(
            datetime_input.get_control(),
            datetime_input_initial.get_control(),
            datetime_input_invalid_initial.get_control(),
            datetime_input_onchange.get_control(),
            ft.ElevatedButton("入力値を確認 (コンソール出力)", on_click=show_value)
        )
        # 最初の描画のために update を呼ぶ
        page.update()

    ft.app(target=main)
