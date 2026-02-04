#!/usr/bin/env python3
"""Test order text parsing."""

def parse_order_text(text: str):
    """
    Parse order from text message sent via ?text= link.
    Format: ORDER:\n1. Name|SKU:xxx|QTYxPRICE=TOTAL\n...\nTOTAL:xxx
    """
    print(f"Input: '{text}'")
    print()

    if not text.startswith('ORDER:'):
        print("ERROR: Does not start with ORDER:")
        return None

    try:
        lines = text.strip().split('\n')
        items = []
        total = 0

        for line in lines:
            line = line.strip()
            print(f"Processing line: '{line}'")

            # Parse item line: "1. Name|SKU:xxx|QTYxPRICE=TOTAL"
            if '|SKU:' in line and '=' in line:
                # Remove number prefix
                if '. ' in line:
                    line = line.split('. ', 1)[1]

                parts = line.split('|')
                print(f"  Parts: {parts}")

                if len(parts) >= 3:
                    name = parts[0].strip()
                    sku = parts[1].replace('SKU:', '').strip()

                    # Parse qty, price from "QTYxPRICE=TOTAL"
                    qty_price = parts[2]
                    if 'x' in qty_price and '=' in qty_price:
                        qty_part = qty_price.split('x')[0]
                        price_part = qty_price.split('x')[1].split('=')[0]
                        qty = int(qty_part) if qty_part.isdigit() else 1
                        price = int(price_part) if price_part.isdigit() else 0
                    else:
                        qty = 1
                        price = 0

                    items.append({
                        'name': name,
                        'sku': sku,
                        'price': price,
                        'qty': qty,
                    })
                    print(f"  ✅ Parsed: {name}, SKU: {sku}, {qty}x{price}")

            # Parse total line
            elif line.startswith('TOTAL:'):
                total_str = line.replace('TOTAL:', '').strip()
                total = int(total_str) if total_str.isdigit() else 0
                print(f"  ✅ Total: {total}")

        if items:
            if total == 0:
                total = sum(item['price'] * item['qty'] for item in items)
            return items, total

    except Exception as e:
        print(f"ERROR: {e}")

    return None


# Test cases
print("=" * 60)
print("TEST 1: Single item")
print("=" * 60)
test1 = """ORDER:
1. Antenna X1|SKU:ANT-001|1x5000=5000
TOTAL:5000"""

result = parse_order_text(test1)
print(f"\nResult: {result}")

print("\n" + "=" * 60)
print("TEST 2: Multiple items")
print("=" * 60)
test2 = """ORDER:
1. Antenna Directional|SKU:ANT-DIR|2x3000=6000
2. RF Module Pro|SKU:RF-MOD|1x12000=12000
TOTAL:18000"""

result = parse_order_text(test2)
print(f"\nResult: {result}")

print("\n" + "=" * 60)
print("TEST 3: URL decoded (what bot receives)")
print("=" * 60)
import urllib.parse
encoded = "ORDER%3A%0A1.%20Antenna%20X1%7CSKU%3AANT-001%7C1x5000%3D5000%0ATOTAL%3A5000"
test3 = urllib.parse.unquote(encoded)
print(f"Decoded from URL: '{test3}'")
result = parse_order_text(test3)
print(f"\nResult: {result}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
