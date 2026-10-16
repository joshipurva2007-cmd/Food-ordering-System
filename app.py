from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, abort, session
)
from database import (
    init_db, create_order, get_all_orders,
    get_pending_orders, get_completed_orders,
    get_order, update_order_status
)

app = Flask(__name__)
app.secret_key = "food-order-system-dev-key"

init_db()

MENU = {
    1: {"name": "Burger", "price": 100},
    2: {"name": "Pizza", "price": 250},
    3: {"name": "Sandwich", "price": 80},
    4: {"name": "French Fries", "price": 90},
    5: {"name": "Coffee", "price": 50},
    6: {"name": "Cold Drink", "price": 40},
}


@app.route("/")
def home():
    return render_template(
        "home.html",
        pending_count=len(get_pending_orders()),
        completed_count=len(get_completed_orders()),
        total_orders=len(get_all_orders())
    )


@app.route("/menu")
def menu():
    return render_template("menu.html", menu=MENU)


@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
        customer_name = request.form.get(
            "customer_name", ""
        ).strip()
        phone = request.form.get("phone", "").strip()

        if not customer_name or not phone:
            flash("Please enter your name and phone number.", "error")
            return redirect(url_for("order"))

        selected_items = []
        total = 0

        for item_id, item in MENU.items():
            try:
                quantity = int(
                    request.form.get(f"quantity_{item_id}", 0)
                )
            except (ValueError, TypeError):
                quantity = 0

            if quantity < 0 or quantity > 100:
                flash("Please enter a valid quantity.", "error")
                return redirect(url_for("order"))

            if quantity > 0:
                subtotal = item["price"] * quantity
                total += subtotal
                selected_items.append(
                    f'{item["name"]} x {quantity} (Rs. {subtotal})'
                )

        if not selected_items:
            flash("Please select at least one food item.", "error")
            return redirect(url_for("order"))

        session["pending_order"] = {
            "customer_name": customer_name,
            "phone": phone,
            "items": ", ".join(selected_items),
            "total": total
        }

        return redirect(url_for("payment"))

    return render_template("order.html", menu=MENU)


@app.route("/payment")
def payment():
    pending_order = session.get("pending_order")

    if not pending_order:
        flash("Please select food items first.", "error")
        return redirect(url_for("order"))

    return render_template(
        "payment.html",
        total=pending_order["total"]
    )


@app.route("/confirm_payment", methods=["POST"])
def confirm_payment():
    pending_order = session.get("pending_order")

    if not pending_order:
        flash("No pending order found. Please order again.", "error")
        return redirect(url_for("order"))

    order_id = create_order(
        pending_order["customer_name"],
        pending_order["phone"],
        pending_order["items"],
        pending_order["total"]
    )

    session.pop("pending_order", None)

    flash(
        f"Demo Payment Successful! Order #{order_id} has been placed.",
        "success"
    )

    return redirect(url_for("bill", order_id=order_id))


@app.route("/queue")
def queue():
    return render_template(
        "queue.html",
        orders=get_pending_orders()
    )


@app.route("/update_status/<int:order_id>", methods=["POST"])
def update_status(order_id):
    status = request.form.get("status", "")
    success = update_order_status(order_id, status)

    if success:
        flash(
            f"Order #{order_id} status updated to {status}.",
            "success"
        )
    else:
        flash(
            "Order not updated. Process orders in FIFO order "
            "and follow Pending → Preparing → Completed.",
            "error"
        )

    return redirect(url_for("queue"))


@app.route("/completed")
def completed():
    return render_template(
        "completed.html",
        orders=get_completed_orders()
    )


@app.route("/history")
def history():
    return render_template(
        "history.html",
        orders=get_all_orders()
    )


@app.route("/bill/<int:order_id>")
def bill(order_id):
    order_data = get_order(order_id)

    if order_data is None:
        abort(404)

    return render_template("bill.html", order=order_data)


@app.errorhandler(404)
def not_found(error):
    return "Page or order not found.", 404


if __name__ == "__main__":
    app.run(debug=True)