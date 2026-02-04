#!/usr/bin/env python3
"""Test payload encoding/decoding between cart.js and bot.py"""
import base64
import json
import urllib.parse

# Simulate cart.js encoding (compact format)
def encode_like_js(items):
    """Encode items like cart.js does"""
    # Compact format: [[id, name, sku, price, qty], ...]
    compact = [
        [
            str(item['id'])[:10],
            item['name'][:30],
            item.get('sku', '')[:15],
            int(item.get('price', 0)),
            int(item.get('qty', 1)),
        ]
        for item in items
    ]
    json_data = json.dumps(compact, separators=(',', ':'))
    print(f"JSON data: {json_data}")
    print(f"JSON length: {len(json_data)}")

    # btoa equivalent with URL-safe base64
    encoded = base64.urlsafe_b64encode(json_data.encode('utf-8')).decode('utf-8')
    # Remove padding like JS does
    encoded = encoded.rstrip('=')
    print(f"Encoded: {encoded}")
    print(f"Encoded length: {len(encoded)}")
    return encoded


# Simulate bot.py decoding
def decode_like_bot(payload):
    """Decode payload like bot.py does"""
    # Add padding
    padding = '=' * (-len(payload) % 4)
    padded = payload + padding
    print(f"Padded: {padded}")

    decoded_raw = base64.urlsafe_b64decode(padded).decode('utf-8')
    print(f"Decoded raw: {decoded_raw}")

    data = json.loads(decoded_raw)
    print(f"Parsed JSON: {data}")

    # Convert compact format
    if isinstance(data, list) and data and isinstance(data[0], list):
        items = []
        for item in data:
            if len(item) >= 5:
                items.append({
                    'id': str(item[0]),
                    'name': str(item[1]),
                    'sku': str(item[2]),
                    'price': int(item[3]) if item[3] else 0,
                    'qty': int(item[4]) if item[4] else 1,
                })
        return items
    return data


print("=" * 60)
print("TEST 1: Single item (should fit in 64 chars)")
print("=" * 60)

test_items_1 = [
    {'id': '1', 'name': 'Antenna X1', 'sku': 'ANT-001', 'price': 5000, 'qty': 1}
]

encoded = encode_like_js(test_items_1)
print(f"\n✅ Fits in 64 chars: {len(encoded) <= 64}")

decoded = decode_like_bot(encoded)
print(f"\nDecoded items: {decoded}")

print("\n" + "=" * 60)
print("TEST 2: Multiple items (may exceed 64 chars)")
print("=" * 60)

test_items_2 = [
    {'id': '1', 'name': 'Antenna Directional', 'sku': 'ANT-DIR-01', 'price': 5000, 'qty': 2},
    {'id': '2', 'name': 'RF Module Pro', 'sku': 'RF-MOD-02', 'price': 12000, 'qty': 1},
]

encoded = encode_like_js(test_items_2)
print(f"\n⚠️ Fits in 64 chars: {len(encoded) <= 64}")

decoded = decode_like_bot(encoded)
print(f"\nDecoded items: {decoded}")

print("\n" + "=" * 60)
print("TEST 3: Generate test URLs")
print("=" * 60)

for test_items, name in [(test_items_1, "1 item"), (test_items_2, "2 items")]:
    encoded = encode_like_js(test_items)
    url_https = f"https://t.me/antidrone_order_bot?start={encoded}"
    url_tg = f"tg://resolve?domain=antidrone_order_bot&start={encoded}"

    print(f"\n{name}:")
    print(f"  Payload length: {len(encoded)}")
    if len(encoded) <= 64:
        print(f"  ✅ HTTPS URL: {url_https}")
    else:
        print(f"  ⚠️ Too long for https://, use tg://")
        print(f"  tg:// URL: {url_tg}")
