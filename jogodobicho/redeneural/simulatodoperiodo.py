import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt

# --- 1. Ler os dados ---
df = pd.read_csv('bichos.csv')
df['bicho_id'] = df['bicho_id'] - 1  # Ajusta para índice 0-24
df = df.sort_values('data')

# --- 2. Preparar sequências ---
N = 10
bicho_ids = df['bicho_id'].values

sequences = []
targets = []
for i in range(len(bicho_ids) - N):
    sequences.append(bicho_ids[i:i+N])
    targets.append(bicho_ids[i+N])

X = np.array(sequences)
y = np.array(targets)

def one_hot_seq(seqs, num_classes=25):
    samples, seq_len = seqs.shape
    one_hot = np.zeros((samples, seq_len, num_classes))
    for i in range(samples):
        for t in range(seq_len):
            one_hot[i, t, seqs[i,t]] = 1
    return one_hot

X_onehot = one_hot_seq(X)
y_onehot = to_categorical(y, num_classes=25)

# --- 3. Criar e treinar modelo ---
model = Sequential()
model.add(LSTM(64, input_shape=(N, 25)))
model.add(Dense(25, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X_onehot, y_onehot, epochs=20, batch_size=32)

# --- 4. Simulação detalhada ---
def simular_apostas_realista_detalhado(model, data, N=10, capital_inicial=1000, meta=2000, aposta_unit=1):
    bichos = data['bicho_id'].values
    capital = capital_inicial
    total_apostas = 0
    acertos = 0
    rodada = 0
    historico = []

    for i in range(len(bichos) - N):
        if capital <= 0:
            print(f'Capital zerado na rodada {rodada}. Parando simulação.')
            break
        if capital >= meta:
            print(f'Meta atingida de R$ {meta} na rodada {rodada}. Parando simulação.')
            break

        seq = bichos[i:i+N]
        real = bichos[i+N]

        x = np.zeros((1, N, 25))
        for t in range(N):
            x[0, t, seq[t]] = 1

        probs = model.predict(x, verbose=0)[0]

        bichos_para_apostar = [idx for idx, p in enumerate(probs) if p * 18 > 1]
        custo = len(bichos_para_apostar) * aposta_unit

        if custo == 0 or custo > capital:
            historico.append({
                'rodada': rodada,
                'bichos_apostados': [],
                'resultado_real': real,
                'acertou': False,
                'capital_apos': capital,
                'total_apostado': total_apostas
            })
            rodada += 1
            continue

        total_apostas += custo
        acertou = real in bichos_para_apostar

        if acertou:
            ganho = 18 * aposta_unit
            capital += ganho - custo
            acertos += 1
        else:
            capital -= custo

        print(f"Rodada {rodada}: Apostou nos bichos {bichos_para_apostar}, resultado: {real}, "
              f"{'Acertou!' if acertou else 'Errou'}, capital agora: R$ {capital:.2f}")

        historico.append({
            'rodada': rodada,
            'bichos_apostados': bichos_para_apostar,
            'resultado_real': real,
            'acertou': acertou,
            'capital_apos': capital,
            'total_apostado': total_apostas
        })

        rodada += 1

    print('--- RESUMO FINAL ---')
    print(f'Capital inicial: R$ {capital_inicial:.2f}')
    print(f'Capital final: R$ {capital:.2f}')
    print(f'Total apostado: R$ {total_apostas:.2f}')
    print(f'Acertos: {acertos}')
    roi = ((capital - capital_inicial) / total_apostas * 100) if total_apostas > 0 else 0
    print(f'ROI: {roi:.2f}%')

    df_historico = pd.DataFrame(historico)
    return df_historico

# --- 5. Executar simulação ---
historico_df = simular_apostas_realista_detalhado(model, df, N=N, capital_inicial=1000, meta=2000, aposta_unit=1)

# --- 6. Exportar histórico para CSV ---
historico_df.to_csv('historico_apostas.csv', index=False)
print('Histórico salvo em historico_apostas.csv')

# --- 7. Plotar evolução do capital ---
plt.figure(figsize=(12,6))
plt.plot(historico_df['rodada'], historico_df['capital_apos'], marker='o')
plt.title('Evolução do Capital nas Rodadas')
plt.xlabel('Rodada')
plt.ylabel('Capital (R$)')
plt.grid(True)
plt.show()
