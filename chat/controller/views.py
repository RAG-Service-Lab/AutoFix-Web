from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST

# 메인 화면
def main(request):
    return render(request, 'main/main.html', {
        'user': request.user  # main.html에서 사용자 정보 접근 가능
    })

def index(request):
    return render(request, 'chat/index.html')


# ---- (데이터 예시: 실제 서비스라면 DB로 전환) ----
VEHICLE_TREE = {
    "현대": {
        "EQ900": ["G 3.5 T-GDI", "G 2.5 T-GDI"],
        "Electrified G80": ["전기모터"],
        "G70": ["G 2.5 T-GDI", "G 3.3 T-GDI"],
        "G80(DH)": ["G 2.5 T-GDI", "G 3.3 T-GDI"],
    },
    "기아": {
        "K9": ["3.3 T-GDI", "3.8 GDI"],
        "스팅어": ["2.5 T-GDI", "3.3 T-GDI"],
    },
}
# ---------------------------------------------

# 채팅 페이지 렌더링
def chat_page(request):
    return render(request, 'chat/chat.html')

# 메인(엔트리) → 분리한 chat.html 렌더
def index(request):
    picked = request.session.get("vehicle", {"maker": "", "model": "", "engine": ""})
    ctx = {
        "makers": list(VEHICLE_TREE.keys()),
        "picked": picked,
    }
    # ⬇️ 분리한 템플릿 경로
    return render(request, "chat/chat.html", ctx)

# (선택) 과거 경로 유지용 별칭
def toggle(request):
    return index(request)

# 옵션 조회 API
@require_GET
def vehicle_options(request):
    maker = request.GET.get("maker")
    model = request.GET.get("model")

    if not maker:
        return JsonResponse({"type": "makers", "data": list(VEHICLE_TREE.keys())})

    if maker and not model:
        models = list(VEHICLE_TREE.get(maker, {}).keys())
        return JsonResponse({"type": "models", "data": models})

    engines = VEHICLE_TREE.get(maker, {}).get(model, [])
    return JsonResponse({"type": "engines", "data": engines})

# 선택 저장 API (세션에 저장)
@require_POST
def set_vehicle(request):
    maker = request.POST.get("maker", "").strip()
    model = request.POST.get("model", "").strip()
    engine = request.POST.get("engine", "").strip()

    if maker not in VEHICLE_TREE:
        return HttpResponseBadRequest("invalid maker")
    if model not in VEHICLE_TREE[maker]:
        return HttpResponseBadRequest("invalid model")
    if engine not in VEHICLE_TREE[maker][model]:
        return HttpResponseBadRequest("invalid engine")

    request.session["vehicle"] = {"maker": maker, "model": model, "engine": engine}
    request.session.modified = True
    label = f"{maker} > {model} > {engine}"
    return JsonResponse({"ok": True, "label": label})

# (선택) 초기화
@require_POST
def clear_vehicle(request):
    request.session.pop("vehicle", None)
    return JsonResponse({"ok": True})


# # ✅ 단일 chat_response (중복 정의 제거!)
# # @require_POST
# def chat_response(request):
#     vehicle = request.session.get("vehicle")
#     if not vehicle or not all(vehicle.get(k) for k in ("maker", "model", "engine")):
#         return JsonResponse({"error": "차량 정보를 먼저 선택해 주세요."}, status=400)

#     user_message = request.POST.get("message", "").strip()
#     if not user_message:
#         return JsonResponse({"error": "메시지가 비어 있습니다."}, status=400)

#     # vehicle_label = f"{vehicle['maker']} > {vehicle['model']} > {vehicle['engine']}"
#     # bot_message = f"[{vehicle_label}] 질문을 확인했어요: \"{user_message}\""
#     return JsonResponse({"response"})

#----------------------------------------------
# import openai

# openai.api_key = "YOUR_OPENAI_API_KEY"


# def toggle(request):
#     picked = request.session.get("vehicle", {"maker": "", "model": "", "engine": ""})
#     ctx = {
#         "makers": list(VEHICLE_TREE.keys()),
#         "picked": picked,
#     }
#     return render(request, "chat/chat.html", ctx)



# AJAX로 채팅 요청 처리
def chat_response(request):
    if request.method == "POST":
        user_message = request.POST.get("message", "")

        # LLM 모델 호출 (예시: GPT)
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "system", "content": "당신은 자동차 고장 진단 전문가입니다."},
        #         {"role": "user", "content": user_message}
        #     ]
        # )

        # answer = response.choices[0].message.content.strip()
        # return JsonResponse({"response": answer})
        
        bot_message = f"'{user_message}' 문제에 대한 분석을 시작합니다..."
        return JsonResponse({"response": bot_message})

    return JsonResponse({"error": "Invalid request"}, status=400)

# # def chat_response(request):
# #     # 나중에 실제 챗봇 응답 로직 넣으면 됨
# #     if request.method == "GET":
# #         return JsonResponse({"message": "GET request received"})
# #     elif request.method == "POST":
# #         return JsonResponse({"message": "POST request received"})
    
