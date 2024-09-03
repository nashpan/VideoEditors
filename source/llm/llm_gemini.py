import logging
import os
from loguru import logger
import traceback

from source.config import get_video_narration_propmt

# 使用google API
import os
from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel, Part

class Gemini:
    def __init__(self):
        vertexai.init(project="ai-bmct", location="us-central1")
        self.__model = GenerativeModel(
            "gemini-1.5-flash",
        )

        self.__bucket_name = "ai-bmct-us"

    def gemini_video_description(self, video_origin_path: str, video_plot: str, language: str) -> str:
        '''
        使用 gemini-1.5-pro 进行影视解析
        Args:
            video_origin_path: str - 影视作品的原始路径
            video_plot: str - 影视作品的简介或剧情概述

        Return:
            str - 解析后的 JSON 格式字符串
        '''

        propmt = get_video_narration_propmt(language, video_plot)

        logger.debug(f"视频名称: {video_origin_path}")
        try:
            source_file_name = video_origin_path
            file_name = os.path.basename(video_origin_path)
            destination_blob_name = f"videos/{file_name}"
            print(destination_blob_name)
            with open("./resource/video_cloud.list", "r") as f:
                lines = f.readlines()
                video_list = [line.replace("\n", "") for line in lines]
            if file_name not in video_list:
                self.__upload_to_gcs(source_file_name, destination_blob_name)
                logger.debug(f"上传视频至 Google cloud 成功: {video_origin_path}")
                with open("./resource/video_cloud.list", "a") as f:
                    f.write(file_name + '\n')
                import time
                time.sleep(1)

        except Exception as err:
            logger.error(f"上传视频至 Google cloud 失败, 请检查 VPN 配置和 APIKey 是否正确 \n{traceback.format_exc()}")
            raise TimeoutError(f"上传视频至 Google cloud 失败, 请检查 VPN 配置和 APIKey 是否正确; {err}")

        video_url = f"gs://{self.__bucket_name}/{destination_blob_name}"
        video_file = Part.from_uri(video_url, mime_type="video/mp4")
        res = self.__model.generate_content([video_file, propmt])

        return res.text

    def gemini_video_align(self, ):

        pass

    def __upload_to_gcs(self, source_file_name, destination_blob_name):
        """Uploads a file to the bucket."""
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.__bucket_name)
        blob = bucket.blob(destination_blob_name)

        # Upload the file
        blob.upload_from_filename(source_file_name)