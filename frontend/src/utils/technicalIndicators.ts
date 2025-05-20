export interface MACDResult {
  dif: number[];
  dea: number[];
  macd: number[];
}

export function calculateMACD(closePrices: number[], shortPeriod = 12, longPeriod = 26, signalPeriod = 9): MACDResult {
  const ema = (prices: number[], period: number): number[] => {
    const k = 2 / (period + 1);
    const emaArray: number[] = [];
    prices.forEach((price, i) => {
      if (i === 0) {
        emaArray.push(price);
      } else {
        emaArray.push(price * k + emaArray[i - 1] * (1 - k));
      }
    });
    return emaArray;
  };

  const emaShort = ema(closePrices, shortPeriod);
  const emaLong = ema(closePrices, longPeriod);

  const dif = emaShort.map((v, i) => v - emaLong[i]);
  const dea = ema(dif, signalPeriod);
  const macd = dif.map((v, i) => 2 * (v - dea[i]));

  return { dif, dea, macd };
}

export interface KDJResult {
  k: number[];
  d: number[];
  j: number[];
}

export function calculateKDJ(
  highPrices: number[],
  lowPrices: number[],
  closePrices: number[],
  period = 9,
  kPeriod = 3,
  dPeriod = 3
): KDJResult {
  const RSV: number[] = [];
  for (let i = 0; i < closePrices.length; i++) {
    if (i < period - 1) {
      RSV.push(50); // 数据不够时默认50
      continue;
    }
    const highMax = Math.max(...highPrices.slice(i - period + 1, i + 1));
    const lowMin = Math.min(...lowPrices.slice(i - period + 1, i + 1));
    const rsv = lowMin === highMax ? 50 : ((closePrices[i] - lowMin) / (highMax - lowMin)) * 100;
    RSV.push(rsv);
  }

  const k: number[] = [];
  const d: number[] = [];
  const j: number[] = [];

  RSV.forEach((rsv, i) => {
    if (i === 0) {
      k.push(50);
      d.push(50);
    } else {
      k.push((k[k.length - 1] * (kPeriod - 1) + rsv) / kPeriod);
      d.push((d[d.length - 1] * (dPeriod - 1) + k[k.length - 1]) / dPeriod);
    }
    j.push(3 * k[i] - 2 * d[i]);
  });

  return { k, d, j };
}