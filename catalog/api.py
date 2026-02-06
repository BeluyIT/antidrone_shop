import json
import re
import secrets
import time
from pathlib import Path

from decouple import config
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST


ORDER_ID_RE = re.compile(r'^[a-z0-9]{8,12}$')


def _generate_order_id(length: int = 10) -> str:
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _build_orders_dir() -> Path:
    orders_dir = Path(settings.BASE_DIR) / 'data' / 'orders'
    orders_dir.mkdir(parents=True, exist_ok=True)
    return orders_dir


def _validate_payload(payload: dict):
    if not isinstance(payload, dict):
        return None, 'Некоректний формат даних.'

    items_raw = payload.get('items', [])
    if not isinstance(items_raw, list) or not items_raw:
        return None, 'Кошик порожній.'

    items: list[dict] = []
    total = 0
    for item in items_raw:
        if not isinstance(item, dict):
            return None, 'Некоректні позиції в кошику.'
        sku = str(item.get('sku', '')).strip()
        name = str(item.get('name', '')).strip() or 'Товар'
        try:
            price = int(item.get('price', 0))
        except (TypeError, ValueError):
            price = 0
        try:
            qty = int(item.get('qty', 0))
        except (TypeError, ValueError):
            qty = 0
        if qty <= 0:
            return None, 'Невірна кількість товару.'
        items.append({
            'sku': sku[:50],
            'name': name[:120],
            'price': price,
            'qty': qty,
        })
        total += price * qty

    currency = str(payload.get('currency') or 'UAH').upper()
    page = str(payload.get('page') or '')
    ts = int(payload.get('ts') or int(time.time() * 1000))
    return items, total, currency, page, ts


def _cleanup_orders(orders_dir: Path, ttl_seconds: int) -> None:
    if ttl_seconds <= 0:
        return
    now = time.time()
    for path in orders_dir.glob('*.json'):
        try:
            if now - path.stat().st_mtime > ttl_seconds:
                path.unlink(missing_ok=True)
        except OSError:
            continue


def _load_order_data(order_id: str):
    if not ORDER_ID_RE.match(order_id):
        return None, JsonResponse({'error': 'Некоректний номер замовлення.'}, status=400)

    orders_dir = _build_orders_dir()
    ttl_hours = max(config('ORDER_TTL_HOURS', default=168, cast=int), 1)
    _cleanup_orders(orders_dir, ttl_hours * 3600)

    order_path = orders_dir / f"{order_id}.json"
    if not order_path.exists():
        return None, JsonResponse({'error': 'Замовлення не знайдено.'}, status=404)

    try:
        with open(order_path, 'r', encoding='utf-8') as handle:
            data = json.load(handle)
    except OSError:
        return None, JsonResponse({'error': 'Не вдалося прочитати замовлення.'}, status=500)

    return data, None


@require_POST
def create_order(request):
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Некоректний JSON.'}, status=400)

    validated = _validate_payload(payload)
    if validated[0] is None:
        return JsonResponse({'error': validated[1]}, status=400)

    items, total, currency, page, ts = validated
    orders_dir = _build_orders_dir()
    ttl_hours = max(config('ORDER_TTL_HOURS', default=168, cast=int), 1)
    _cleanup_orders(orders_dir, ttl_hours * 3600)

    order_id = _generate_order_id()
    for _ in range(5):
        order_path = orders_dir / f"{order_id}.json"
        if not order_path.exists():
            break
        order_id = _generate_order_id()
    else:
        return JsonResponse({'error': 'Не вдалося створити замовлення.'}, status=500)

    order_data = {
        'order_id': order_id,
        'items': items,
        'total': total,
        'currency': currency,
        'source': payload.get('source', 'site'),
        'page': page,
        'ts': ts,
        'status': 'new',
        'created_at': int(time.time()),
    }

    try:
        with open(order_path, 'w', encoding='utf-8') as handle:
            json.dump(order_data, handle, ensure_ascii=False, indent=2)
    except OSError:
        return JsonResponse({'error': 'Не вдалося зберегти замовлення.'}, status=500)

    if not order_path.exists():
        return JsonResponse({'error': 'Не вдалося створити замовлення.'}, status=500)

    return JsonResponse({'order_id': order_id})


def get_order(request, order_id: str):
    data, error = _load_order_data(order_id)
    if error:
        return error

    response = {
        'order_id': data.get('order_id', order_id),
        'items': data.get('items', []),
        'total': data.get('total', 0),
        'currency': data.get('currency', 'UAH'),
        'ts': data.get('ts', 0),
        'source': data.get('source', 'site'),
    }
    return JsonResponse(response)


@require_POST
def confirm_order(request, order_id: str):
    data, error = _load_order_data(order_id)
    if error:
        return error

    orders_dir = _build_orders_dir()
    order_path = orders_dir / f"{order_id}.json"
    data['status'] = 'confirmed'
    data['confirmed_at'] = int(time.time())
    try:
        with open(order_path, 'w', encoding='utf-8') as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
    except OSError:
        return JsonResponse({'error': 'Не вдалося оновити замовлення.'}, status=500)

    return JsonResponse({'order_id': order_id, 'status': 'confirmed'})
