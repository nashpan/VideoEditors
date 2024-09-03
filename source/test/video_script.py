'''
测试内容: gemini的视频理解能力
说明: 输入一个视频, 输出对于这个视频的理解
'''


from source.llm.llm_gemini import Gemini

gemini = Gemini()

video_path = ""
language = ""
video_plot = ""
res = gemini.gemini_video_description(video_path, video_plot, language)
print(res)