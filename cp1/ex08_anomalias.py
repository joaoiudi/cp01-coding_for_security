"""
Exercício 8 — Detecção de anomalias (IsolationForest)
Features: [requisicoes_min, conexoes_simultaneas]
"""
import numpy as np
from sklearn.ensemble import IsolationForest

TRAFEGO = np.array([
    [100, 5], [120, 6], [110, 5], [105, 4],
    [50000, 500], [109, 5], [111, 6], [45000, 450],
])


def main():
    modelo = IsolationForest(contamination=0.25, random_state=42)
    pred = modelo.fit_predict(TRAFEGO)      # -1 = anomalia, 1 = normal
    scores = modelo.score_samples(TRAFEGO)  # quanto menor, mais anômalo

    anomalias = []
    for i, (amostra, p, s) in enumerate(zip(TRAFEGO, pred, scores)):
        if p == -1:
            print(f"Amostra {i}: [{amostra[0]}, {amostra[1]}] -> ANOMALIA (score {s:.3f})")
            anomalias.append(i)
        else:
            print(f"Amostra {i}: [{amostra[0]}, {amostra[1]}] -> Normal")

    print(f"\nTotal de anomalias detectadas: {len(anomalias)} de {len(TRAFEGO)} amostras")


if __name__ == "__main__":
    main()
