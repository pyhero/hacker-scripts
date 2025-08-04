import os
import sys
import yaml
import json
import datetime
from collections import OrderedDict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def ordered_yaml_load(yaml_path, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """
    Desc: ordered yaml loader
    Args:
        yaml_path: the path of yaml file to load

    Returns: ordered dict

    """
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)

    with open(yaml_path, encoding='utf-8') as stream:
        return yaml.load(stream, OrderedLoader)


def ordered_yaml_dump(data, stream=None, Dumper=yaml.SafeDumper, **kwds):
    """
    Desc: ordered yaml dumper
    Args:
        data: dict data

    Returns: ordered yaml data

    """
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    OrderedDumper.ignore_aliases = lambda self, data: True

    return yaml.dump(data, stream, OrderedDumper, width=2048, **kwds)


def yaml_reader(yaml_file):
    """
    Desc: ordered yaml reader
    Args:
        yaml_file: the path of yaml file to read

    Returns: ordered dict

    """
    if not os.path.exists(yaml_file):
        raise Exception('{}: not exist.'.format(yaml_file))

    contents = ordered_yaml_load(yaml_file)

    return contents


def yaml_writer(contents, yaml_file):
    """
    Desc: ordered yaml writer
    Args:
        contents: ordered dict
        yaml_file: the path of yaml file to write

    Returns: the path of yaml file

    """
    contents = ordered_yaml_dump(contents, default_flow_style=False)
    with open(yaml_file, 'w', encoding='utf-8') as f:
        f.write(contents)

    return yaml_file


class HackerInstallment(object):
    def __init__(self, installments_list):
        self.installments_list = installments_list
        self.today = datetime.datetime.now()
        self.current_month = "{}-{:02d}".format(self.today.year, self.today.month)

    def sorted_dict(self, d):
        return dict(sorted(d.items(), key=lambda x: x[0]))

    def sort_by_end_date(self, items):
        def get_end_date_key(obj):
            if isinstance(obj, str):
                end_date_str = obj.split('~')[1].split('：')[0].strip()
                year, month = map(int, end_date_str.split('-'))
                return year * 12 + month
            elif isinstance(obj, dict):
                key = next(iter(obj.keys()))
                end_date_str = key.split('~')[1].split('：')[0].strip()
                year, month = map(int, end_date_str.split('-'))
                return year * 12 + month

        return sorted(items, key=get_end_date_key)

    def round_floats(self, obj):
        if isinstance(obj, dict):
            return {k: self.round_floats(v) for k, v in obj.items()}
        elif isinstance(obj, (int, float)):
            return round(float(obj), 2)
        elif isinstance(obj, (list, tuple)):
            return type(obj)(self.round_floats(item) for item in obj)
        else:
            return obj

    def add_months(self, date, n=1):
        if isinstance(date, str):
            date_obj = datetime.datetime.strptime(date, '%Y-%m')
        else:
            date_obj = date

        year = date_obj.year
        month = date_obj.month

        new_month = month + n
        new_year = year + new_month // 12
        new_month %= 12

        if new_month == 0:
            new_month = 12
            new_year -= 1

        new_date_obj = datetime.date(new_year, new_month, 1)
        new_date_str = new_date_obj.strftime('%Y-%m')

        return new_date_str

    def month_diff(self, date_str1, date_str2):
        year1, month1 = map(int, date_str1.split('-'))
        year2, month2 = map(int, date_str2.split('-'))
        total_months1 = year1 * 12 + month1
        total_months2 = year2 * 12 + month2

        return abs(total_months2 - total_months1)

    def date_str_to_year(self, date_str):
        year_str = date_str.split('-')[0]
        return year_str

    def hacker_print(self, contents):
        if isinstance(contents, (dict, list)):
            print(json.dumps(contents, indent=2, ensure_ascii=False))
        else:
            print(contents)

    def generate_loan_list(self):
        debt = dict()

        for x in self.installments_list:
            key = x['first_repayment_month']
            value = (x['total_installment_amount'], x['monthly_interest'] * x['number_of_installments'])

            if key in debt:
                debt[key].append(value)
            else:
                debt[key] = [value]

        loan = dict()

        for month, amount in debt.items():
            year = self.date_str_to_year(month)

            if year not in loan:
                loan[year] = dict()
                loan[year]['total'] = amount[0][0] + amount[0][1]
                loan[year]['principal'] = amount[0][0]
                loan[year]['interest'] = amount[0][1]

                if len(amount) > 1:
                    for a in amount[1:]:
                        loan[year]['total'] += a[0] + a[1]
                        loan[year]['principal'] += a[0]
                        loan[year]['interest'] += a[1]
            else:
                for a in amount:
                    loan[year]['total'] += a[0] + a[1]
                    loan[year]['principal'] += a[0]
                    loan[year]['interest'] += a[1]
        
        return self.sorted_dict(loan)

    def analyze_loan(self):
        loan = self.generate_loan_list()
        loan_info = {
            "info": {
                'total': round(sum((x['total'] for x in loan.values())), 2),
                'principal': round(sum((x['principal'] for x in loan.values())), 2),
                'interest': round(sum((x['interest'] for x in loan.values())), 2),
            },
            "detail": loan
        }

        return loan_info

    def analyze_bills(self):
        paied_bills = list()
        unpaied_bills = list()
        paied_info = {
            "total": {
                "amount": 0,
                "principal": 0,
                "interest": 0,
            }
        }
        unpaied_info = {
            "total": {
                "amount": 0,
                "principal": 0,
                "interest": 0,
            },
            "paied": {
                "amount": 0,
                "principal": 0,
                "interest": 0,
            },
            "unpaied": {
                "amount": 0,
                "principal": 0,
                "interest": 0,
            },
        }

        for installment in self.installments_list:
            first_repayment_month = installment['first_repayment_month']
            last_repayment_month = self.add_months(first_repayment_month, installment['number_of_installments'] - 1)
            total_installment_amount = installment['total_installment_amount']
            monthly_payment = installment['monthly_payment']
            monthly_interest = installment['monthly_interest']
            number_of_installments = installment['number_of_installments']
            bill_key = "{} ~ {}：{} / {}".format(first_repayment_month, last_repayment_month, total_installment_amount, number_of_installments)

            # if all(bill_key not in x.keys() for x in current_month_repayment):
            if last_repayment_month < self.current_month:
                paied_bills.append(bill_key)
                paied_info['total']['amount'] += total_installment_amount + number_of_installments * monthly_interest
                paied_info['total']['principal'] += total_installment_amount
                paied_info['total']['interest'] += number_of_installments * monthly_interest
            else:
                unpaied_bills.append(bill_key)
                unpaied_info['total']['amount'] += total_installment_amount + number_of_installments * monthly_interest
                unpaied_info['total']['principal'] += total_installment_amount
                unpaied_info['total']['interest'] += number_of_installments * monthly_interest

                paied_months = self.month_diff(self.current_month, first_repayment_month)
                unpaied_info['paied']['amount'] += (monthly_payment + monthly_interest) * paied_months
                unpaied_info['paied']['principal'] += monthly_payment * paied_months
                unpaied_info['paied']['interest'] += monthly_interest * paied_months

                unpaied_months = self.month_diff(self.current_month, last_repayment_month) + 1
                unpaied_info['unpaied']['amount'] += (monthly_payment + monthly_interest) * unpaied_months
                unpaied_info['unpaied']['principal'] += monthly_payment * unpaied_months
                unpaied_info['unpaied']['interest'] += monthly_interest * unpaied_months
        
        paied_info['bills'] = self.sort_by_end_date(paied_bills)
        unpaied_info['bills'] = self.sort_by_end_date(unpaied_bills)

        bills = {
            "paied_bills": paied_info,
            "unpaied_bills": unpaied_info
        }

        return bills

    def generate_monthly_repayments(self):
        _monthly_bills = dict()

        for installment in self.installments_list:
            for num in range(installment['number_of_installments']):
                repayment_month = self.add_months(installment['first_repayment_month'], num)
                _key = "{} ~ {}：{} / {}".format(
                    installment['first_repayment_month'],
                    self.add_months(installment['first_repayment_month'], installment['number_of_installments'] - 1),
                    installment['total_installment_amount'],
                    installment['number_of_installments'],
                )
                _value = installment['monthly_payment'] + installment['monthly_interest']

                if repayment_month in _monthly_bills:
                    _monthly_bills[repayment_month].append({_key: _value})
                else:
                    _monthly_bills[repayment_month] = [{_key: _value}]

        monthly_bills = self.round_floats(_monthly_bills)

        return monthly_bills

    def analyze_repayments_plan(self, plan_months=-1):
        monthly_repayments = self.generate_monthly_repayments()
        max_month = max(monthly_repayments.keys())
        plan = dict()
        n = 0
        
        while True:
            if plan_months > -1 and n >= plan_months:
                break

            next_month = self.add_months(self.current_month, n)

            if next_month > max_month:
                break


            plan[next_month] = self.sort_by_end_date(monthly_repayments[next_month])
            plan[next_month].insert(0, {'amount': sum((list(i.values())[0] for i in plan[next_month]))})
            n += 1

        return plan

    def main(self):
        plan_months = 3

        info = self.round_floats({
            "贷款信息": self.analyze_loan(),
            "还款情况": self.analyze_bills(),
            # "未来计划": self.analyze_repayments_plan(plan_months)
            "未来计划": {k: [f"{next(iter(item.keys()))}: {item[next(iter(item.keys()))]:.2f}" for item in v] for k, v in self.analyze_repayments_plan(plan_months).items()}
        })
        
        self.hacker_print(info)


if __name__ == '__main__':
    # installments = [
    #     {
    #         "total_installment_amount": 20000,
    #         "monthly_payment": 1666.66,
    #         "monthly_interest": 51.33,
    #         "number_of_installments": 12,
    #         "first_repayment_month": "2025-01"
    #     },
    # ]

    installments_yaml_file_path = "/Users/bytedance/Documents/intallments.yml"
    installments = yaml_reader(installments_yaml_file_path)

    hi = HackerInstallment(installments)
    hi.main()
