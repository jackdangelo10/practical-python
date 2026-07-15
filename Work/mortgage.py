# mortgage.py
## mortgage.py

principal = 500000.0
rate = 0.05
payment = 2684.11
total_paid = 0.0
month = 0
extra_amount_current = 0
extra_payment = 1000
extra_payment_start_month = 61
extra_payment_end_month = 108

while principal > 0:
    month = month + 1
    if month <= extra_payment_end_month and month >= extra_payment_start_month :
        extra_amount_current = extra_payment
    else: 
        extra_amount_current = 0
    principal = principal * (1+rate/12) - payment - extra_amount_current
    total_paid = total_paid + payment + extra_amount_current
    print(f"{month} {round(total_paid, 2)} {round(principal, 2)}")

print('Total paid', round(total_paid,2))
print('Expected months:', month)
# Exercise 1.7
