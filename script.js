window.onload = function() {
    const totalTrades = document.getElementById("totalTrades");

const totalProfit = document.getElementById("totalProfit");

const winRate = document.getElementById("winRate");
    const marketMood = document.getElementById("marketMood");

const confidenceValue = document.getElementById("confidenceValue");
    
const btc = document.getElementById("btcPrice");

const signalText = document.getElementById("signalText");

const rsiValue = document.getElementById("rsiValue");

console.log(rsiValue);

// BTC PRICE

async function loadBTCPrice() {

    const response = await fetch(
        "https://aiquant-2hiv.onrender.com/btc-price"
    );

    const data = await response.json();

    btc.innerHTML = `$${data.bitcoin_price}`;
}


// RSI SIGNAL

async function loadRSI() {

    const response = await fetch(
        "https://aiquant-2hiv.onrender.com/btc-rsi"
    );

    const data = await response.json();

    signalText.innerHTML = data.signal;

    rsiValue.innerHTML = `RSI: ${data.rsi}`;


    if(data.signal === "BUY") {

        signalText.style.color = "lime";

    }

    else if(data.signal === "SELL") {

        signalText.style.color = "red";

    }

    else {

        signalText.style.color = "yellow";

    }

}


// START

loadBTCPrice();

loadRSI();


// AUTO REFRESH

setInterval(loadBTCPrice, 10000);

setInterval(loadRSI, 5000);
const balanceValue = document.getElementById("balanceValue");

const positionValue = document.getElementById("positionValue");

const actionValue = document.getElementById("actionValue");

const tradeTable = document.getElementById("tradeTable");


async function loadPaperTrade(){

    const response = await fetch(
        "https://aiquant-2hiv.onrender.com/paper-trade"
    );

    const data = await response.json();

    balanceValue.innerHTML = `$${data.balance}`;

    positionValue.innerHTML = data.position || "NONE";

    actionValue.innerHTML = data.action;
    tradeTable.innerHTML = "";

data.trade_history.forEach(trade => {

    const row = `

        <tr>

            <td class="${trade.type === 'BUY' ? 'buy' : 'sell'}">
                ${trade.type}
            </td>

            <td>
                $${trade.price}
            </td>

            <td>
                ${trade.profit ? "$" + trade.profit : "-"}
            </td>

        </tr>

    `;

    tradeTable.innerHTML += row;

});
}


loadPaperTrade();

setInterval(loadPaperTrade, 5000);
async function loadAISentiment() {

    const response = await fetch(
        "https://aiquant-2hiv.onrender.com/ai-sentiment"
    );

    const data = await response.json();

    marketMood.innerHTML = data.mood;

    confidenceValue.innerHTML = `${data.confidence}%`;


    if(data.mood === "BULLISH") {

        marketMood.style.color = "lime";

    }

    else if(data.mood === "BEARISH") {

        marketMood.style.color = "red";

    }

    else {

        marketMood.style.color = "yellow";

    }

}


loadAISentiment();

setInterval(loadAISentiment, 5000);
async function loadPerformance() {

    const response = await fetch(
        "https://aiquant-2hiv.onrender.com/performance"
    );

    const data = await response.json();

    totalTrades.innerHTML = data.total_trades;

    totalProfit.innerHTML = `$${data.total_profit}`;

    winRate.innerHTML = `${data.win_rate}%`;


    if(data.total_profit >= 0) {

        totalProfit.style.color = "lime";

    }

    else {

        totalProfit.style.color = "red";

    }

}


loadPerformance();

setInterval(loadPerformance, 5000);
const ctx = document.getElementById("pnlChart");

let pnlChart = null;


async function loadEquityCurve() {

    const response = await fetch(
        "https://aiquant-2hiv.onrender.com/equity-curve"
    );

    const data = await response.json();

    const labels = data.equity.map((_, index) => index + 1);


    if(pnlChart) {

        pnlChart.destroy();

    }


    pnlChart = new Chart(ctx, {

        type: "line",

        data: {

            labels: labels,

            datasets: [{

                label: "Portfolio Balance",

                data: data.equity,

                borderColor: "#00bfff",

                backgroundColor: "rgba(0,191,255,0.2)",

                tension: 0.4,

                fill: true

            }]
        },

        options: {

            responsive: true
        }
    });
}


loadEquityCurve();

setInterval(loadEquityCurve, 5000);
}