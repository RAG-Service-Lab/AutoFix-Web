import requests
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST, require_http_methods

# FASTAPI_URL = "http://127.0.0.1:8001/query"
FASTAPI_URL = "http://194.68.245.121:8000/query"

@require_http_methods(["GET", "POST"])
def chat_response(request):
    if request.method == "GET":
        # 페이지 렌더(브라우저로 직접 /chat/response/ 열 때)
        picked = request.session.get("brand", {"maker":"", "model":"", "engine":""})
        vehicle_summary = ""
        if all(picked.get(k) for k in ("maker","model","engine")):
            vehicle_summary = f'{picked["maker"]} > {picked["model"]} > {picked["engine"]}'
        return render(request, "chat/chat.html", {"vehicle_summary": vehicle_summary})
        # return render(request, "chat/chat.html", {"picked": picked})

    # POST: AJAX 응답(JSON)
    msg = request.POST.get("message", "").strip()
    if not msg:
        return JsonResponse({"error": "메시지가 비어 있습니다."}, status=400)

    bot_message = f"'{msg}' 문제에 대한 분석을 시작합니다..."

    payload = {
        "query": msg,
        "session_id": f"{request.user.username}"
    }

    try:
        res = requests.post(FASTAPI_URL, json=payload, timeout=60)
        res.raise_for_status()
        data = res.json()
        bot_message = data.get("output", "응답을 불러오지 못했습니다.")
    except Exception as e:
        bot_message = f"FastAPI 서버 호출 오류: {str(e)}"

    return JsonResponse({"response": bot_message}, json_dumps_params={"ensure_ascii": False})


from django.http import JsonResponse
from django.urls import reverse

def set_vehicle(request):
    if request.method == 'POST':
        maker = request.POST.get('maker')
        model = request.POST.get('model')
        engine = request.POST.get('engine')

        # 세션에 저장
        request.session['maker'] = maker
        request.session['model'] = model
        request.session['engine'] = engine

        # 채팅 페이지 URL 생성
        chat_url = reverse('chat:chat_page')
        return JsonResponse({'ok': True, 'chat_url': chat_url})

    return JsonResponse({'ok': False, 'error': 'Invalid request'})

# 긴급연락|보험사 모달
def info_content(request):
    return render(request, 'chat/info_content.html')  # Ajax로 불러올 모달 내용