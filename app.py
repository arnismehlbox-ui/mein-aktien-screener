dist_52h = round(((cp - high_52) / high_52) * 100, 1)

                    scan_results.append({
                        "Ticker": sym,
                        "Kurs": round(cp, 2),
                        "24h (%)": round(chg, 2),
                        "RSI (14)": rsi,
                        "Trend (SMA)": trend,
                        "Abst. 52W-Hoch": f"{dist_52h}%"
                    })
            except:
                pass
        
        if scan_results:
            df_res = pd.DataFrame(scan_results)
            st.dataframe(df_res, use_container_width=True)

# -------------------------------------------------------------------
# TRADINGVIEW CHART (FULLSCREEN ADAPTIVE WITH STRATEGY INDICATORS)
# -------------------------------------------------------------------
def get_tradingview_widget(ticker, strat):
    # Mapping Tickers for TV
    tv_symbol = ticker
    if ".DE" in ticker:
        tv_symbol = f"XETR:{ticker.replace('.DE', '')}"
    elif ticker in ["NVDA", "AAPL", "GOOGL", "MSFT", "AMZN", "META", "TSLA", "AMD", "PLTR"]:
        tv_symbol = f"NASDAQ:{ticker}"
    else:
        tv_symbol = f"NYSE:{ticker}"

    # Adaptive Studies based on Strategy
    studies = ["MASimple@tv-basicstudies"]
    if "Momentum" in strat:
        studies = ["RSI@tv-basicstudies", "MACD@tv-basicstudies"]
    elif "Volumen" in strat:
        studies = ["Volume@tv-basicstudies", "VPVR@tv-basicstudies"]
    elif "Swing" in strat:
        studies = ["STD;EMA", "RSI@tv-basicstudies"]

    studies_js = str(studies).replace("'", '"')

    return f"""
    <div class="tradingview-widget-container" style="height:100%;width:100%;">
      <div id="tradingview_chart" style="height:580px;width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "autosize": true,
        "symbol": "{tv_symbol}",
        "interval": "D",
        "timezone": "Europe/Berlin",
        "theme": "dark",
        "style": "1",
        "locale": "de_DE",
        "toolbar_bg": "#1e222d",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "details": false,
        "hotlist": false,
        "calendar": false,
        "studies": {studies_js},
        "container_id": "tradingview_chart"
      }}
      );
      </script>
    </div>
    """

components.html(get_tradingview_widget(st.session_state.selected_ticker, strategy), height=585, scrolling=False)
