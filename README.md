# Subapka
App for managing subscriptions
Version 1.0

## API

### Format wymiany danych

Wszystkie żądania i odpowiedzi używają formatu **JSON** (UTF-8).

- Żądania z treścią (POST, PUT, PATCH) wysyłają nagłówek `Content-Type: application/json`.
- Lista rekordów: `{"items": [ ... ]}`
- Pojedynczy rekord (GET, PUT, PATCH): `{"items": { ... }}`
- POST `/users` i `/subscriptions`: `{"ok": true, "id": 5}`, gdzie `id` to identyfikator nowego rekordu
- POST `/types`: utworzony typ, `{"items": {"name": "...", "label": "..."}}`
- **PUT** podmienia cały rekord wszystkie pola są wymagane.
- **PATCH** zmienia tylko przesłane pola, pozostałe zostają bez zmian.
- Dane wejściowe są walidowane (zobacz [Walidacja](#walidacja)). Niepoprawne dane zwracają 422.
- Daty: `"YYYY-MM-DD"`, zapis czasu: (`"2026-11-07T23:55:42"`).
- Kwoty (`price`) w żądaniu jako liczba lub tekst (`23.99` albo `"23.99"`), w odpowiedzi jako liczba.

Przykład:

```bash
curl -X PATCH http://localhost:3000/api/subscriptions/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "cancelled"}'
```

```json
{
  "items": {
    "id": 1,
    "name": "Spotify",
    "price": 23.99,
    "currency": "PLN",
    "type": "monthly",
    "renewal_date": "2026-12-05",
    "user_id": 2,
    "status": "cancelled",
    "created_at": "2026-11-07T23:55:42"
  }
}
```

### Błędy

Błędy zwracają JSON z polem `detail`:

```json
{"detail": "Nie ma takiego uzytkownika"}
```

| Kod | Opis |
|---|---|
| 400 | Duplikat (np. email), nieznany typ lub użytkownik, pusty PATCH |
| 404 | Rekord o podanym id / nazwie nie istnieje |
| 422 | Dane nie przechodzą walidacji (brak wymaganego pola, zły typ danych, za krótki tekst, cena ≤ 0 itd.) |

### Walidacja

Dane wejściowe są sprawdzane przez modele Pydantic (`Field`) przed zapytaniem do bazy. Reguły dla każdego pola są opisane w tabelach przy poszczególnych zasobach.

- Te same reguły obowiązują w POST, PUT i PATCH. W PATCH sprawdzane są tylko przesłane pola.
- W PATCH pola z wartością `null` są pomijane. Jeśli nie zostaje żadne pole do zmiany, API zwraca 400 (`Brak pol do aktualizacji`).
- Nieznane pola w body są ignorowane.
- Przy 422 `detail` jest listą błędów: `loc` wskazuje pole, a `msg` opisuje problem.
- Unikalność (`name` i `email` użytkownika, `name` typu) oraz istnienie typu i użytkownika w subskrypcji sprawdza baza. Naruszenie zwraca 400, nie 422.

### Health

| Metoda | Ścieżka | Odpowiedź |
|---|---|---|
| GET | `/health` | `{"status": "up"}` |

### Użytkownicy: `/users`

Obiekt użytkownika:

```json
{"id": 1, "name": "ala", "email": "ala@example.com", "created_at": "2026-11-07T23:55:42"}
```

| Pole | Typ | Walidacja |
|---|---|---|
| `id` | int | nadawane przez bazę, tylko w odpowiedzi |
| `name` | string | 1–100 znaków, unikalne |
| `email` | string | format `nazwa@domena.pl` (bez spacji, z `@` i kropką w domenie), max 255 znaków, unikalny |
| `password` | string | 8–128 znaków, tylko w żądaniu |
| `created_at` | znacznik czasu | nadawany przez bazę, tylko w odpowiedzi |

| Metoda | Ścieżka | Body | Odpowiedź | Błędy |
|---|---|---|---|---|
| GET | `/users` | — | lista użytkowników | |
| GET | `/users/{id}` | — | użytkownik | 404 |
| POST | `/users` | `name`, `email`, `password` | `{"ok": true, "id": ...}` | 400, 422 |
| PUT | `/users/{id}` | `name`, `email`, `password` | zaktualizowany użytkownik | 400, 404, 422 |
| PATCH | `/users/{id}` | dowolne z: `name`, `email`, `password` | zaktualizowany użytkownik | 400, 404, 422 |

`name` i `email` muszą być unikalne (inaczej 400).

POST `/users`:

```json
{"name": "ala", "email": "ala@example.com", "password": "tajnehaslo"}
```

Odpowiedź:

```json
{"ok": true, "id": 1}
```

PATCH `/users/1`:

```json
{"email": "nowy@example.com"}
```

### Typy subskrypcji: `/types`

```json
{"name": "monthly", "label": "co miesiac"}
```

Domyślnie w bazie są typy `weekly`, `monthly` i `yearly`.

| Pole | Typ | Walidacja |
|---|---|---|
| `name` | string | 1–50 znaków, unikalna, identyfikator typu |
| `label` | string | 1–100 znaków, wymagany (nie może być pusty ani `null`) |

| Metoda | Ścieżka | Body | Odpowiedź | Błędy |
|---|---|---|---|---|
| GET | `/types` | — | lista typów | |
| GET | `/types/{name}` | — | typ | 404 |
| POST | `/types` | `name`, `label` | utworzony typ | 400, 422 |
| PUT | `/types/{name}` | `label` | zaktualizowany typ | 404, 422 |
| PATCH | `/types/{name}` | `label` (opcjonalnie) | zaktualizowany typ | 400, 404, 422 |

Nazwy typu nie da się zmienić: PUT i PATCH zmieniają tylko `label`.

PUT `/types/monthly`:

```json
{"label": "miesięcznie"}
```

### Subskrypcje: `/subscriptions`

| Pole | Typ | Walidacja |
|---|---|---|
| `id` | int | nadawane przez bazę, tylko w odpowiedzi |
| `name` | string | min. 1 znak |
| `price` | liczba | > 0, 2 miejsca po przecinku |
| `currency` | string | dokładnie 3 znaki, np. `PLN`, `EUR` |
| `type` | string | min. 1 znak, `name` istniejącego typu z `/types` (inaczej 400) |
| `renewal_date` | data | `YYYY-MM-DD` |
| `user_id` | int | id istniejącego użytkownika (inaczej 400) |
| `status` | string | `active` albo `cancelled` |
| `created_at` | znacznik czasu | nadawany przez bazę, tylko w odpowiedzi |

| Metoda | Ścieżka | Body | Odpowiedź | Błędy |
|---|---|---|---|---|
| GET | `/subscriptions` | — | lista subskrypcji | 422 |
| GET | `/subscriptions/{id}` | — | subskrypcja | 404 |
| POST | `/subscriptions` | wszystkie pola, `status` opcjonalny (domyślnie `active`) | `{"ok": true, "id": ...}` | 400, 422 |
| PUT | `/subscriptions/{id}` | wszystkie pola, łącznie ze `status` | zaktualizowana subskrypcja | 400, 404, 422 |
| PATCH | `/subscriptions/{id}` | dowolne z pól | zaktualizowana subskrypcja | 400, 404, 422 |

GET `/subscriptions` przyjmuje opcjonalne filtry w query stringu: `user_id` i `status`, np. `/subscriptions?user_id=2&status=active`. Niepoprawna wartość filtra (np. `status=paused`) zwraca 422. Wyniki są posortowane po `renewal_date`, a potem po `id`.

POST `/subscriptions`:

```json
{
  "name": "Netflix",
  "price": 43.00,
  "currency": "PLN",
  "type": "monthly",
  "renewal_date": "2026-12-01",
  "user_id": 2
}
```

GET `/subscriptions?user_id=2`:

```json
{
  "items": [
    {
      "id": 1,
      "name": "Netflix",
      "price": 43.0,
      "currency": "PLN",
      "type": "monthly",
      "renewal_date": "2026-12-01",
      "user_id": 2,
      "status": "active",
      "created_at": "2026-11-07T23:55:42"
    }
  ]
}
```
