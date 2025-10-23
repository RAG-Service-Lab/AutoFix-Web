# chat/toggles_views.py
from django.http import JsonResponse
from django.shortcuts import render

# ---- 예시 데이터 (DB 연동 전 테스트용) ----
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

def toggles_page(request):
    """
    토글 페이지 렌더링 (드롭다운 3개)
    """
    picked = request.session.get("vehicle", {"maker": "", "model": "", "engine": ""})
    makers = list(VEHICLE_TREE.keys())
    return render(request, "chat/toggles.html", {"makers": makers, "picked": picked})


def vehicle_options(request):
    """
    AJAX: 의존형 셀렉트용 데이터 반환
    - ?maker=현대        -> {"type":"models",  "data":[...]}
    - ?maker=현대&model=G70 -> {"type":"engines","data":[...]}
    """
    maker = request.GET.get("maker")
    model = request.GET.get("model")

    if not maker:
        return JsonResponse({"type": "error", "data": []}, status=400)

    # 모델 목록
    if maker and not model:
        models = list(VEHICLE_TREE.get(maker, {}).keys())
        return JsonResponse({"type": "models", "data": models})

    # 엔진 목록
    if maker and model:
        engines = VEHICLE_TREE.get(maker, {}).get(model, [])
        return JsonResponse({"type": "engines", "data": engines})

    return JsonResponse({"type": "error", "data": []}, status=400)


def set_vehicle_and_go_chat(request):
    """
    엔진까지 선택 완료 후 호출(POST).
    세션에 저장하고 채팅 페이지로 이동시키기 위한 URL을 내려준다.
    """
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)

    maker = request.POST.get("maker", "")
    model = request.POST.get("model", "")
    engine = request.POST.get("engine", "")

    if not (maker and model and engine):
        return JsonResponse({"ok": False, "msg": "invalid"}, status=400)

    request.session["vehicle"] = {"maker": maker, "model": model, "engine": engine}
    label = f"{maker} > {model} > {engine}"
    # 프론트에서 이 url로 location.href 이동
    from django.urls import reverse
    chat_url = reverse("chat:chat_page")
    return JsonResponse({"ok": True, "label": label, "chat_url": chat_url})
