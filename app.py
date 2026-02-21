import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from flask import Flask, request, render_template
import mysql.connector

# -------- Load Dataset --------
data = pd.read_csv("gold_loan.csv")

data['ExistingLoan'] = data['ExistingLoan'].map({'Yes':1,'No':0})
data['Status'] = data['Status'].map({'Approve':1,'Reject':0})

X = data.drop("Status", axis=1)
y = data["Status"]

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2)

# -------- Train Model --------
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# -------- Flask App --------
app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def home():
    if request.method == "POST":
        weight = float(request.form["weight"])
        purity = float(request.form["purity"])
        income = float(request.form["income"])
        credit = int(request.form["credit"])
        loan = float(request.form["loan"])
        existing = 1 if request.form["existing"] == "Yes" else 0

        result = model.predict([[weight, purity, income, credit, loan, existing]])
        prediction = "Approved" if result[0]==1 else "Rejected"

        # Save to MySQL
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="95974",
            database="goldloan"
        )

        cursor = db.cursor()
        sql = """
        INSERT INTO applications
        (weight, purity, income, credit_score, loan_amount, existing_loan, prediction)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """
        values = (weight, purity, income, credit, loan, existing, prediction)
        cursor.execute(sql, values)
        db.commit()

        return render_template("index.html", prediction_text=f"Loan {prediction}")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)