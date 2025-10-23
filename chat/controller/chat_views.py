from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST

    


# def toggle(request):
#     picked = request.session.get("vehicle", {"maker": "", "model": "", "engine": ""})
#     ctx = {
#         "makers": list(VEHICLE_TREE.keys()),
#         "picked": picked,
#     }
#     return render(request, "chat/chat.html", ctx)

# 채팅 페이지 렌더링
def chat_page(request):
    picked = request.session.get("vehicle", {"maker": "", "model": "", "engine": ""})
    label = ""
    if picked["maker"] and picked["model"] and picked["engine"]:
        label = f'{picked["maker"]} > {picked["model"]} > {picked["engine"]}'
    return render(request, "chat/chat.html", {"vehicle_label": label})
    # return render(request, 'chat/chat.html')

def chat_response(request):
    if request.method == "POST":
        msg = request.POST.get("message", "")
        # 여기에 모델 호출 로직 넣으면 됨
        return JsonResponse({"response": f"'{msg}' 문제에 대한 분석을 시작합니다..."})
    return JsonResponse({"error": "Invalid request"}, status=400)

# # AJAX로 채팅 요청 처리
# @require_POST
# def chat_response(request):
#     if request.method == "POST":
#         user_message = request.POST.get("message", "")

#         user_message = request.POST.get("message", "").strip()
#         # 필요하면 maker/model/engine도 사용 가능
#         maker  = request.POST.get("maker", "")
#         model  = request.POST.get("model", "")
#         engine = request.POST.get("engine", "")


#         # LLM 모델 호출 (예시: GPT)
#         # response = openai.ChatCompletion.create(
#         #     model="gpt-3.5-turbo",
#         #     messages=[
#         #         {"role": "system", "content": "당신은 자동차 고장 진단 전문가입니다."},
#         #         {"role": "user", "content": user_message}
#         #     ]
#         # )

#         # answer = response.choices[0].message.content.strip()
#         # return JsonResponse({"response": answer})
        
#         bot_message = f"'{user_message}' 문제에 대한 분석을 시작합니다..."
#         return JsonResponse({"response": bot_message})

#     return JsonResponse({"error": "Invalid request"}, status=400)

# # def chat_response(request):
# #     # 나중에 실제 챗봇 응답 로직 넣으면 됨
# #     if request.method == "GET":
# #         return JsonResponse({"message": "GET request received"})
# #     elif request.method == "POST":
# #         return JsonResponse({"message": "POST request received"})
