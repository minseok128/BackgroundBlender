from PIL import Image
import sys
import os
from datetime import datetime
import urllib.request
import base64
import json
import time
import os

webui_server_url = "http://127.0.0.1:3000"


def encode_file_to_base64(path):
    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def decode_and_save_base64(base64_str, save_path):
    with open(save_path, "wb") as file:
        file.write(base64.b64decode(base64_str))


def call_api(api_endpoint, **payload):
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{webui_server_url}/{api_endpoint}",
        headers={"Content-Type": "application/json"},
        data=data,
    )
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode("utf-8"))


def call_img2img_api(save_path, **payload):
    response = call_api("sdapi/v1/img2img", **payload)
    for index, image in enumerate(response.get("images")):
        save_path = os.path.join(save_path, f"img2img-{datetime.fromtimestamp(time.time()).strftime("%Y%m%d-%H%M%S")}-{index}.png")
        decode_and_save_base64(image, save_path)


def create_prepared_image(image_path, size_x, size_y, pos_x, pos_y):
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
                masked_pixels.append((0, 0, 0, 255))
            else:
                masked_pixels.append((255, 255, 255, 255))
        masked_image = Image.new("RGBA", new_image.size)
        masked_image.putdata(masked_pixels)
        masked_image.save(os.path.join(temp_dir, "img2.png"), "PNG")

    except FileNotFoundError:
        print(f"오류: 파일 {image_path}를 찾을 수 없습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")


def generate_image(save_path):
    init_images = [
        encode_file_to_base64(r"./tmp/img1.png"),
    ]
    batch_size = 2
    payload = {
        "prompt": "1girl, blue hair",
        "seed": 1,
        "steps": 20,
        "width": 512,
        "height": 512,
        "denoising_strength": 0.5,
        "n_iter": 1,
        "init_images": init_images,
        "batch_size": batch_size if len(init_images) == 1 else len(init_images),
        "mask": encode_file_to_base64("./tmp/img2.png"),
    }
    call_img2img_api(save_path, **payload)


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

        create_prepared_image(image_path, size_x, size_y, pos_x, pos_y)
        generate_image(save_path)

    except ValueError:
        print("오류: 올바른 숫자 값을 입력하세요.")
        sys.exit(1)

