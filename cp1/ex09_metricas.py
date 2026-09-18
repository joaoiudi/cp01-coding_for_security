"""
Exercício 9 — Métricas honestas em dataset desbalanceado
"""
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score, precision_score, recall_score,
)

y_true = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1]   # 8 normais, 2 ataques
y_pred = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]   # o modelo perdeu 1 ataque


def main():
    matriz = confusion_matrix(y_true, y_pred)
    print(f"Matriz: {matriz.tolist()}")
    tn, fp, fn, tp = matriz.ravel()
    print(f"  VN={tn}  FP={fp}  FN={fn}  VP={tp}")

    print(
        f"\nAcurácia: {accuracy_score(y_true, y_pred):.2f} | "
        f"Precisão: {precision_score(y_true, y_pred):.2f} | "
        f"Recall: {recall_score(y_true, y_pred):.2f} | "
        f"F1: {f1_score(y_true, y_pred):.2f}"
    )

    # Comentário: a acurácia de 0.90 só é alta porque 8 das 10 amostras são da classe
    # majoritária (normal) — um modelo que dissesse "normal" para tudo já acertaria 0.80.
    # O recall de 0.50 revela o que importa em segurança: METADE dos ataques passou batido
    # (1 falso negativo). Em base desbalanceada, recall e F1 são as métricas que contam.
    print(
        "\nComentário: acurácia 0.90 mascara que METADE dos ataques passou (recall 0.50)."
    )


if __name__ == "__main__":
    main()
