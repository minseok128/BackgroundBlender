from PIL import Image
import sys
import os


def create_image(image_path, size_x, size_y, pos_x, pos_y, save_path):
    temp_dir = "./tmp/"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        input_image = Image.open(image_path).convert("RGBA")
        new_image = Image.new("RGBA", (size_x, size_y), (0, 0, 0, 0))
        new_image.paste(input_image, (pos_x, pos_y), input_image)
        new_image.save(os.path.join(temp_dir, "img1.png"), "PNG")

        pixels = new_image.getdata()
        masked_pixels = []
        for pixel in pixels:
            if pixel == (0, 0, 0, 0):
                masked_pixels.append((255, 255, 255, 255))
            else:
                masked_pixels.append((0, 0, 0, 0))
        masked_image = Image.new("RGBA", new_image.size)
        masked_image.putdata(masked_pixels)
        masked_image.save(os.path.join(temp_dir, "img2.png"), "PNG")

    except FileNotFoundError:
        print(f"오류: 파일 {image_path}를 찾을 수 없습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python main.py <이미지 주소>")
        sys.exit(1)

    image_path = sys.argv[1]

    try:
        image_caption = (
            input("제품에 대한 설명을 입력하세요 (기본: wine glass): ") or "wine glass"
        )

        size_x_input = input("생성할 이미지의 너비를 입력하세요 (기본: 1024): ")
        size_x = int(size_x_input) if size_x_input else 1024

        size_y_input = input("생성할 이미지의 높이를 입력하세요 (기본: 1024): ")
        size_y = int(size_y_input) if size_y_input else 1024

        pos_x_input = input("인풋 이미지의 x 좌표를 입력하세요 (기본: 300): ")
        pos_x = int(pos_x_input) if pos_x_input else 300

        pos_y_input = input("인풋 이미지의 y 좌표를 입력하세요 (기본: 300): ")
        pos_y = int(pos_y_input) if pos_y_input else 300

        save_path = (
            input("저장할 파일 이름을 입력하세요 (기본: output.png): ") or "output.png"
        )

        bg_prompt = (
            input("제품의 배경에 대해서 묘사하세요 (기본: 해변가): ")
            or image_caption
            + " on a sandy beach, clear blue sky, photorealistic, 8k, highly detailed, trending on artstation"
        )
    except ValueError:
        print("오류: 올바른 숫자 값을 입력하세요.")
        sys.exit(1)

    create_image(image_path, size_x, size_y, pos_x, pos_y, save_path)
