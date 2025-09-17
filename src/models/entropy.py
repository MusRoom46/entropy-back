import math
import re
import string
from collections import Counter, defaultdict


def calculate_entropy(username: str, password: str) -> dict:
    """
    Vérifie la robustesse du mot de passe en reprenant
    les mêmes critères que le front (regex, entropie bits, redondance).

    Retour :
        dict :
        - "valid" (bool) : si toutes les conditions sont respectées
        - "errors" (list[str]) : règles non respectées
        - "entropy_bits" (float) : estimation bits d'entropie
        - "redundancy" (float) : redondance finale [0..1]
        - "redundancy_percent" (int) : redondance finale en %
        - "components" (dict) : valeurs R1, R2, R3 détaillées
    """

    errors = []

    # Regex de validation (12+ chars, maj, min, chiffre, symbole)
    regex = re.compile(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()\-=+\[\]{};:'\",.<>\/\\?`~|]).{12,}$"
    )
    if not regex.match(password):
        if len(password) < 12:
            errors.append("Le mot de passe doit contenir au moins 12 caractères.")
        if not re.search(r"[a-z]", password):
            errors.append("Le mot de passe doit contenir au moins une minuscule.")
        if not re.search(r"[A-Z]", password):
            errors.append("Le mot de passe doit contenir au moins une majuscule.")
        if not re.search(r"\d", password):
            errors.append("Le mot de passe doit contenir au moins un chiffre.")
        if not re.search(r"[!@#$%^&*()\-=+\[\]{};:'\",.<>\/\\?`~|]", password):
            errors.append("Le mot de passe doit contenir au moins un caractère spécial.")

    # ==== Entropie globale (comme dans le front) ====
    def estimate_entropy_bits(pwd: str) -> int:
        if not pwd:
            return 0
        charset = 0
        if re.search(r"[a-z]", pwd):
            charset += 26
        if re.search(r"[A-Z]", pwd):
            charset += 26
        if re.search(r"\d", pwd):
            charset += 10
        if re.search(r"[!@#$%^&*()\-=+\[\]{};:'\",.<>\/\\?`~|]", pwd):
            charset += 33
        if re.search(r"\s", pwd):
            charset += 1
        if charset == 0:
            return 0
        bits_per_char = math.log2(charset)
        return round(len(pwd) * bits_per_char)

    entropy_bits = estimate_entropy_bits(password)

    # ==== Redondance (R1, R2, R3) ====

    # R1 : diversité (fréquences empiriques)
    def distinct_char_count(pwd: str) -> int:
        return len(set(pwd)) if pwd else 0

    def empirical_entropy_per_char(pwd: str) -> float:
        n = len(pwd)
        if n == 0:
            return 0.0
        freq = Counter(pwd)
        h = 0.0
        for count in freq.values():
            p = count / n
            h += -p * math.log2(p)
        return h

    # R2 : dépendances séquentielles
    def conditional_entropy_rate_selective(pwd: str, min_trans=2) -> float:
        n = len(pwd)
        if n <= 1:
            return 0.0
        trans = defaultdict(Counter)
        prev_cnt = Counter()
        for i in range(1, n):
            a, b = pwd[i - 1], pwd[i]
            trans[a][b] += 1
            prev_cnt[a] += 1
        reliable = {a: nexts for a, nexts in trans.items() if prev_cnt[a] >= min_trans}
        tot_prev_rel = sum(prev_cnt[a] for a in reliable)
        if not reliable:
            return empirical_entropy_per_char(pwd)
        H = 0.0
        for a, nexts in reliable.items():
            sum_next = sum(nexts.values())
            pPrev = prev_cnt[a] / tot_prev_rel
            Ha = sum(-c / sum_next * math.log2(c / sum_next) for c in nexts.values())
            H += pPrev * Ha
        return H

    # R3 : couverture des blocs répétés
    def repeated_block_coverage(pwd: str) -> float:
        n = len(pwd)
        if n < 4:
            return 0.0
        best = 0
        Lmax = min(n // 2, 8)
        for L in range(Lmax, 1, -1):
            for i in range(n - 2 * L + 1):
                block = pwd[i : i + L]
                j, reps = i + L, 1
                while j + L <= n and pwd[j : j + L] == block:
                    reps += 1
                    j += L
                if reps >= 2:
                    covered = reps * L
                    best = max(best, covered)
            if best == n:
                break
        return best / n

    k_distinct = distinct_char_count(password)
    h_max = math.log2(k_distinct) if k_distinct > 0 else 0.0
    h_emp = empirical_entropy_per_char(password)
    h_rate_sel = conditional_entropy_rate_selective(password, 2)

    R1 = 1 - min(h_emp, h_max) / h_max if h_max > 0 else 1.0
    R2 = 1 - min(h_rate_sel, h_max) / h_max if h_max > 0 else 1.0
    R3 = repeated_block_coverage(password)

    # pondération comme dans le front
    W_R1, W_R2 = 0.3, 0.2
    redundancy = max(R3, W_R1 * R1, W_R2 * R2)
    redundancy_percent = round(100 * max(0, min(1, redundancy)))

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "entropy_bits": entropy_bits,
        "redundancy": redundancy,
        "redundancy_percent": redundancy_percent,
        "components": {
            "R1": R1,
            "R2": R2,
            "R3": R3,
        },
    }
