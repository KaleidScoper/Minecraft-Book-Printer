import re
import argparse
import time
import sys
import logging
from typing import List, Dict
import win32api
import win32con
import pyautogui
import pyperclip
import os

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BookConfig:
    """书本格式配置类"""

    def __init__(
            self,
            lines_per_page: int = 14,
            max_line_width: float = 57.0,
            char_widths: Dict[str, float] = None,
            chinese_punctuation: List[str] = None
    ):
        self.lines_per_page = lines_per_page
        self.max_line_width = max_line_width
        self.char_widths = char_widths or self.default_char_widths()
        self.chinese_punctuation = chinese_punctuation or self.default_chinese_punctuation()

    @staticmethod
    def default_char_widths() -> Dict[str, float]:
        return {
            '`': 1.5,
            '[': 2, ']': 2, '(': 2, ')': 2, '"': 2, '{': 2, '}': 2, '*': 2, ' ': 2,
            '.': 1, ',': 1, ';': 1, ':': 1, "'": 1, '!': 1, '|': 1,
            '<': 2.5, '>': 2.5,
            '→': 4, '~': 4,
            '\n': -1
        }

    @staticmethod
    def default_chinese_punctuation() -> List[str]:
        return [
            '，', '。', '、', '？', '！', '】', '【', '（', '）',
            '·', '；', '：', '“', '‘', '《', '》', '…'
        ]


class TextFormatter:
    """文本格式化处理类"""

    def __init__(self, config: BookConfig):
        self.config = config

    def is_chinese(self, char: str) -> bool:
        """判断字符是否为中文或中文标点"""
        if char in self.config.chinese_punctuation:
            return True
        return re.match(r'[\u4e00-\u9fff]', char) is not None

    def get_char_width(self, char: str) -> float:
        """获取字符宽度"""
        if char in self.config.char_widths:
            return self.config.char_widths[char]
        if self.is_chinese(char):
            return 4.5
        return 3.0  # 默认英文字符宽度

    def split_into_lines(self, text: str) -> List[str]:
        """将文本分割为符合宽度限制的行"""
        current_line = []
        current_width = 0.0
        lines = []

        for char in text:
            char_width = self.get_char_width(char)

            if char == '\n':
                lines.append(''.join(current_line))
                current_line = []
                current_width = 0.0
                continue

            if current_width + char_width > self.config.max_line_width:
                lines.append(''.join(current_line))
                current_line = [char]
                current_width = char_width
            else:
                current_line.append(char)
                current_width += char_width

        if current_line:
            lines.append(''.join(current_line))

        return self._process_trailing_newlines(text, lines)

    def _process_trailing_newlines(self, original: str, lines: List[str]) -> List[str]:
        """处理原始文本末尾的换行符"""
        if original.endswith('\n'):
            while lines and lines[-1] == '':
                lines.pop()
            if lines:
                lines[-1] = lines[-1].rstrip('\n')
        return lines

    def format_pages(self, lines: List[str]) -> List[str]:
        """将行列表分页处理"""
        pages = []
        current_page = []

        for line in lines:
            current_page.append(line)
            if len(current_page) >= self.config.lines_per_page:
                pages.append('\n'.join(current_page))
                current_page = []

        if current_page:
            pages.append('\n'.join(current_page))

        return pages


class InputHandler:
    """输入处理类"""

    def __init__(self, delay: float = 0.2, offset_x: int = -50, offset_y: int = -50):
        self.delay = delay
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.abort_key = 0x1B  # ESC键虚拟键码

    def wait_for_trigger(self, trigger_key: int = win32con.VK_CONTROL):
        """等待指定触发键按下"""
        logger.info("等待Ctrl键按下（按ESC取消）...")
        while True:
            if win32api.GetAsyncKeyState(self.abort_key) & 0x8000:
                logger.warning("检测到ESC键，程序终止")
                sys.exit(0)
            if win32api.GetAsyncKeyState(trigger_key) & 0x8000:
                logger.info("检测到Ctrl键，开始输入")
                return
            time.sleep(self.delay)

    def simulate_input(self, pages: List[str]):
        """
        模拟键盘输入：每页：
        1. 聚焦输入框
        2. 粘贴内容
        3. 点击翻页按钮
        """

        logger.info("开始自动输入，每页输入前先聚焦输入框，然后点击翻页按钮")

        original_pos = pyautogui.position()
        try:
            for idx, page in enumerate(pages, 1):
                # 1) 鼠标向左上偏移，点击输入框确保聚焦
                focus_pos = (original_pos[0] + self.offset_x, original_pos[1] + self.offset_y)
                pyautogui.moveTo(focus_pos)
                pyautogui.click()
                time.sleep(self.delay)

                # 2) 复制到剪贴板并粘贴
                pyperclip.copy(page)
                time.sleep(0.2)  # 给系统时间更新剪贴板
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.3)

                logger.debug(f"已输入第{idx}/{len(pages)}页")

                # 3) 如果不是最后一页，点击翻页按钮（回到原位置点击）
                if idx < len(pages):
                    pyautogui.moveTo(original_pos)
                    pyautogui.click()
                    logger.debug("已点击翻页按钮")
                    time.sleep(self.delay)

        except Exception as e:
            logger.error(f"输入过程中发生错误: {str(e)}")
            raise


def main(path='input.txt'):
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="自动格式化文本为Minecraft书本格式")
    parser.add_argument('input', nargs='?', default=path,
                        help="输入文件路径（默认为input.txt）")
    parser.add_argument('--lines', type=int, default=14,
                        help="每页行数（默认为14）")
    parser.add_argument('--preview', action='store_true',
                        help="仅预览分页结果不执行输入")
    parser.add_argument('--verbose', action='store_true',
                        help="显示详细调试信息")
    parser.add_argument('--offset_x', type=int, default=-50,
                        help="鼠标聚焦点X偏移（默认-50）")
    parser.add_argument('--offset_y', type=int, default=-50,
                        help="鼠标聚焦点Y偏移（默认-50）")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    config = BookConfig(lines_per_page=args.lines)
    formatter = TextFormatter(config)
    input_handler = InputHandler(delay=0.3, offset_x=args.offset_x, offset_y=args.offset_y)

    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        input_file = os.path.join(base_dir, args.input)

        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()

        # ✅ 文本预处理：合并多余换行
        text = re.sub(r'\n{2,}', '\n\n', text.strip())

        lines = formatter.split_into_lines(text)
        pages = formatter.format_pages(lines)

        if args.preview:
            logger.info(f"预览模式（共{len(pages)}页）:")
            for i, page in enumerate(pages, 1):
                print(f"\n=== 第{i}页 ===")
                print(page)
                print("=" * 20)
            return

        logger.info(f"共处理{len(pages)}页文本（每页{args.lines}行）")
        logger.info("切换到游戏窗口后，按住Ctrl键开始自动输入...")

        input_handler.wait_for_trigger()
        input_handler.simulate_input(pages)
        logger.info("所有内容输入完成")

    except FileNotFoundError:
        logger.error(f"输入文件不存在: {input_file}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"发生未预期错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main("input.txt")
