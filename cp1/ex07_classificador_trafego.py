"""
Exercício 7 — Classificador de tráfego (RandomForestClassifier)
Features: [bytes, porta, duracao] | Rótulos: 0 = normal, 1 = malicioso
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

X = np.array([
    [500, 80, 0.1], [1200, 80, 0.5], [64, 22, 0.02], [64000, 4444, 10.0], [45000, 8080, 15.0],
    [60000, 31337, 20.0], [800, 443, 0.3], [300, 53, 0.05], [55000, 9999, 18.0], [200, 25, 0.2],
])
y = np.array([0, 0, 0, 1, 1, 1, 0, 0, 1, 0])
CASO_NOVO = [[58000, 4444, 16.0]]


def main():
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    modelo = RandomForestClassifier(random_state=42)   # random_state fixo = reprodutível
    modelo.fit(X_train, y_train)

    acuracia = accuracy_score(y_test, modelo.predict(X_test))
    print(f"Acurácia no teste: {acuracia:.2f}")

    pred = modelo.predict(CASO_NOVO)[0]
    rotulo = "Malicioso" if pred == 1 else "Normal"
    print(f"Caso novo {CASO_NOVO[0]} -> {rotulo} ({pred})")

    prob = modelo.predict_proba(CASO_NOVO)[0][1]
    print(f"Confiança de ser malicioso: {prob:.2f}")

    nomes = ["bytes", "porta", "duracao"]
    print("\nImportância das features:")
    for nome, imp in zip(nomes, modelo.feature_importances_):
        print(f"  {nome:8s} {imp:.3f}")


if __name__ == "__main__":
    main()
