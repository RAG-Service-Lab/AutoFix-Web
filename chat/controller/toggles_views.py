# chat/toggles_views.py
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

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
    picked = request.session.get("vehicle", {"maker": "", "model": "", "engine": ""})
    vehicle_summary = ""
    if all(picked.get(k) for k in ("maker","model","engine")):
        vehicle_summary = f'{picked["maker"]} > {picked["model"]} > {picked["engine"]}'
    context = { "makers": ["현대", "기아"], "picked": picked, "vehicle_summary": vehicle_summary}
    return render(request, "chat/toggles.html", context)


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
    maker = request.POST.get("maker")
    model = request.POST.get("model")
    engine = request.POST.get("engine")
    if not (maker and model and engine):
        return JsonResponse({"ok": False, "error": "모든 항목을 선택해야 합니다."})
    
    request.session["vehicle"] = {"maker": maker, "model": model, "engine": engine}
    chat_url = reverse("chat:chat_response")
    return JsonResponse({"ok": True, "chat_url": chat_url})
