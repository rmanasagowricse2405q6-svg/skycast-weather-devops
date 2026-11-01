from flask import Flask, jsonify, render_template, request
import requests

CODES={0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",45:"Fog",48:"Rime fog",51:"Light drizzle",53:"Drizzle",55:"Heavy drizzle",61:"Light rain",63:"Moderate rain",65:"Heavy rain",71:"Light snow",73:"Moderate snow",75:"Heavy snow",80:"Rain showers",81:"Moderate rain showers",82:"Heavy rain showers",95:"Thunderstorm",96:"Thunderstorm with hail",99:"Severe thunderstorm"}
def create_app():
    app=Flask(__name__)
    @app.get("/")
    def home(): return render_template("index.html")
    @app.get("/health")
    def health(): return jsonify(status="ok"),200
    @app.get("/api/weather")
    def weather():
        city=request.args.get("city","").strip()
        if not city: return jsonify(error="Please enter a city name."),400
        if len(city)>100: return jsonify(error="City name is too long."),400
        try:
            g=requests.get("https://geocoding-api.open-meteo.com/v1/search",params={"name":city,"count":1,"language":"en","format":"json"},timeout=8)
            g.raise_for_status(); places=g.json().get("results",[])
            if not places: return jsonify(error=f"No location found for '{city}'. Try another spelling."),404
            p=places[0]
            r=requests.get("https://api.open-meteo.com/v1/forecast",params={"latitude":p["latitude"],"longitude":p["longitude"],"current":"temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m","daily":"weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max","timezone":"auto","forecast_days":5},timeout=10)
            r.raise_for_status(); d=r.json(); c=d["current"]; daily=d["daily"]
            days=[]
            for i,date in enumerate(daily.get("time",[])):
                code=daily["weather_code"][i]
                days.append({"date":date,"weather_code":code,"description":CODES.get(code,"Unknown conditions"),"max":daily["temperature_2m_max"][i],"min":daily["temperature_2m_min"][i],"rain_chance":daily["precipitation_probability_max"][i]})
            code=c.get("weather_code")
            return jsonify(location={"name":p.get("name",city),"region":p.get("admin1",""),"country":p.get("country","")},current={"temperature":c.get("temperature_2m"),"feels_like":c.get("apparent_temperature"),"humidity":c.get("relative_humidity_2m"),"wind_speed":c.get("wind_speed_10m"),"precipitation":c.get("precipitation"),"weather_code":code,"description":CODES.get(code,"Unknown conditions"),"is_day":c.get("is_day")},daily=days,source="Open-Meteo")
        except requests.RequestException:
            app.logger.exception("Weather provider request failed")
            return jsonify(error="Weather service is temporarily unavailable. Please try again."),502
        except (KeyError,TypeError,ValueError,IndexError):
            app.logger.exception("Unexpected weather provider response")
            return jsonify(error="The weather service returned an unexpected response."),502
    return app
app=create_app()
if __name__=="__main__": app.run(host="0.0.0.0",port=5000)
