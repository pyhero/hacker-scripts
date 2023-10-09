import argparse
from copy import deepcopy

class MortgageSmartCalculator(object):
    def __init__(self, loan_amount, loan_term, interest_rate, repayment_month_serial_number=60, *args, **kwargs):
        # 贷款本金
        self.loan_amount = loan_amount * 10000
        # 贷款年限
        self.loan_term = loan_term
        # 还款月数
        self.terms_duration_of_loan = loan_term * 12
        # 年利率
        self.interest_rate = interest_rate
        # 月利率
        self.monthly_interest_rate = interest_rate / 12
        # 还款月序号
        self.repayment_month_serial_number = repayment_month_serial_number

        self.args = args
        self.kwargs = kwargs

        print("贷款金额: {}; 贷款年限: {} (即 {} 个月)".format(
            round(self.loan_amount),
            loan_term,
            self.terms_duration_of_loan
        ))

    def matching_the_principal_repayment(self):
        """
        等额本金还款
        """
        finally_res = dict()
        # 每月应还本金
        the_principal_should_be_repaid_every_month = self.loan_amount / self.terms_duration_of_loan
        # 剩余本金
        residual_principal = deepcopy(self.loan_amount)
        # 已归还本金累计额
        the_cumulative_amount_of_principal_has_been_repaid = 0
        # 还款月序号
        repayment_month_serial_number = 0

        for _year in range(1, self.loan_term + 1):
            finally_res[_year] = dict()

            for _month in range(1, 13):
                # 月供
                monthly_payment = (self.loan_amount / self.terms_duration_of_loan) + (self.loan_amount - the_cumulative_amount_of_principal_has_been_repaid) * self.monthly_interest_rate
                # 当月应还利息
                interest_is_due_during_the_month = residual_principal * self.monthly_interest_rate
                # 已归还本金累计额
                the_cumulative_amount_of_principal_has_been_repaid += the_principal_should_be_repaid_every_month
                # 剩余本金
                residual_principal -= the_principal_should_be_repaid_every_month
                # 还款月序号
                repayment_month_serial_number += 1

                finally_res[_year][_month] = {
                    "monthly_payment": round(monthly_payment),
                    "the_principal_has_be_repaid_during_the_month": round(the_principal_should_be_repaid_every_month),
                    "interest_is_due_during_the_month": round(interest_is_due_during_the_month),
                    "repayment_month_serial_number": repayment_month_serial_number
                }

        return finally_res

    def equal_principal_and_interest_repayment(self):
        """
        等额本息还款
        """
        finally_res = dict()
        # 月供
        monthly_payment = (self.loan_amount * self.monthly_interest_rate * (1 + self.monthly_interest_rate) ** self.terms_duration_of_loan) / ((1 + self.monthly_interest_rate) ** self.terms_duration_of_loan - 1)
        # 还款月序号
        repayment_month_serial_number = 0

        for _year in range(1, self.loan_term + 1):
            finally_res[_year] = dict()

            for _month in range(1, 13):
                # 还款月序号
                repayment_month_serial_number += 1
                # 当月应还利息
                interest_is_due_during_the_month = self.loan_amount * self.monthly_interest_rate * ((1 + self.monthly_interest_rate) ** self.terms_duration_of_loan - (1 + self.monthly_interest_rate) ** (repayment_month_serial_number - 1)) / ((1 + self.monthly_interest_rate) ** self.terms_duration_of_loan - 1)
                # 当月应该本金
                the_principal_should_be_repaid_during_the_month = self.loan_amount * self.monthly_interest_rate * (1 + self.monthly_interest_rate) ** (repayment_month_serial_number - 1) / ((1 + self.monthly_interest_rate) ** self.terms_duration_of_loan - 1)

                finally_res[_year][_month] = {
                    "monthly_payment": round(monthly_payment),
                    "the_principal_has_be_repaid_during_the_month": round(the_principal_should_be_repaid_during_the_month),
                    "interest_is_due_during_the_month": round(interest_is_due_during_the_month),
                    "repayment_month_serial_number": repayment_month_serial_number
                }

        return finally_res

    def _transfer_data_to_list(self, repayment_data):
        _data_lists = {
            "monthly_payment": [
                _month_data['monthly_payment']
                for _month_details in repayment_data.values()
                for _month_data in _month_details.values()
            ],
            "the_principal_has_be_repaid_during_the_month": [
                _month_data['the_principal_has_be_repaid_during_the_month']
                for _month_details in repayment_data.values()
                for _month_data in _month_details.values()
            ],
            "interest_is_due_during_the_month": [
                _month_data['interest_is_due_during_the_month']
                for _month_details in repayment_data.values()
                for _month_data in _month_details.values()
            ],
            "repayment_month_serial_number": [
                _month_data['repayment_month_serial_number']
                for _month_details in repayment_data.values()
                for _month_data in _month_details.values()
            ],
        }

        return _data_lists

    def _split_data_lists_by_repayment_month_serial_number(self, repayment_data_lists):
        _res = {
            k: v[:self.repayment_month_serial_number]
            for k, v in repayment_data_lists.items()
        }

        return _res

    def _sum(self, repayment_data_lists):
        _res = {
            k: sum(v)
            for k, v in repayment_data_lists.items()
        }

        return _res
    
    def _max(self, repayment_data_lists):
        _res = {
            k: (max(v), v.index(max(v)) if len(set(v)) > 1 else 0)
            for k, v in repayment_data_lists.items()
        }

        return _res

    def _min(self, repayment_data_lists):
        _res = {
            k: (min(v), v.index(min(v)) if len(set(v)) > 1 else len(v) - 1)
            for k, v in repayment_data_lists.items()
        }

        return _res

    def _parse(self, repayment_data):
        _repayment_data_lists = self._transfer_data_to_list(repayment_data)
        _sum_info = self._sum(_repayment_data_lists)
        _repayment_month_serial_number_data_lists = self._split_data_lists_by_repayment_month_serial_number(_repayment_data_lists)
        _repayment_month_serial_number_sum_info = self._sum(_repayment_month_serial_number_data_lists)

        if len(set(_repayment_data_lists['monthly_payment'])) > 1:
            message_list = [
                "\t共需还约: {}, 本金共: {}, 利息共约: {}".format(
                    _sum_info['monthly_payment'],
                    int(self.loan_amount),
                    _sum_info['interest_is_due_during_the_month'],
                ),
                "\t  最大还款月为【第 {} 月】, 月供金额约: {}, 本金约 {}, 利息约 {}".format(
                    _repayment_data_lists['repayment_month_serial_number'][0],
                    _repayment_data_lists['monthly_payment'][0],
                    _repayment_data_lists['the_principal_has_be_repaid_during_the_month'][0],
                    _repayment_data_lists['interest_is_due_during_the_month'][0],
                ),
                "\t  最还小款月为【第 {} 月】, 月供金额约: {}, 本金约 {}, 利息约 {}".format(
                    _repayment_data_lists['repayment_month_serial_number'][-1],
                    _repayment_data_lists['monthly_payment'][-1],
                    _repayment_data_lists['the_principal_has_be_repaid_during_the_month'][-1],
                    _repayment_data_lists['interest_is_due_during_the_month'][-1],
                ),
                "\n\t截止到第 {} 个月, 共偿还约 {}, 本金约: {}, 利息约: {}".format(
                    self.repayment_month_serial_number,
                    _repayment_month_serial_number_sum_info['monthly_payment'],
                    _repayment_month_serial_number_sum_info['the_principal_has_be_repaid_during_the_month'],
                    _repayment_month_serial_number_sum_info['interest_is_due_during_the_month'],
                ),
                "\t  最大还款月为【第 {} 月】, 月供金额约: {}, 本金约 {}, 利息约 {}".format(
                    _repayment_month_serial_number_data_lists['repayment_month_serial_number'][0],
                    _repayment_month_serial_number_data_lists['monthly_payment'][0],
                    _repayment_month_serial_number_data_lists['the_principal_has_be_repaid_during_the_month'][0],
                    _repayment_month_serial_number_data_lists['interest_is_due_during_the_month'][0],
                ),
                "\t  最还小款月为【第 {} 月】, 月供金额约: {}, 本金约 {}, 利息约 {}".format(
                    _repayment_month_serial_number_data_lists['repayment_month_serial_number'][-1],
                    _repayment_month_serial_number_data_lists['monthly_payment'][-1],
                    _repayment_month_serial_number_data_lists['the_principal_has_be_repaid_during_the_month'][-1],
                    _repayment_month_serial_number_data_lists['interest_is_due_during_the_month'][-1],
                ),
            ]
        else:
            message_list = [
                "\t共需还约: {}, 本金共: {}, 利息共约: {}".format(
                    _sum_info['monthly_payment'],
                    int(self.loan_amount),
                    _sum_info['interest_is_due_during_the_month'],
                ),
                "\t  利息最高月为【第 {} 月】, 月供金额约: {}, 本金约 {}, 利息约 {}".format(
                    _repayment_data_lists['repayment_month_serial_number'][0],
                    _repayment_data_lists['monthly_payment'][0],
                    _repayment_data_lists['the_principal_has_be_repaid_during_the_month'][0],
                    _repayment_data_lists['interest_is_due_during_the_month'][0],
                ),
                "\t  利息最低月为【第 {} 月】, 月供金额约: {}, 本金约 {}, 利息约 {}".format(
                    _repayment_data_lists['repayment_month_serial_number'][-1],
                    _repayment_data_lists['monthly_payment'][-1],
                    _repayment_data_lists['the_principal_has_be_repaid_during_the_month'][-1],
                    _repayment_data_lists['interest_is_due_during_the_month'][-1],
                ),
                "\n\t截止到第 {} 个月, 共偿还约 {}, 本金约: {}, 利息约: {}".format(
                    self.repayment_month_serial_number,
                    _repayment_month_serial_number_sum_info['monthly_payment'],
                    _repayment_month_serial_number_sum_info['the_principal_has_be_repaid_during_the_month'],
                    _repayment_month_serial_number_sum_info['interest_is_due_during_the_month'],
                ),
                "\t  利息最高月为【第 {} 月】, 月供金额约: {}, 本金约 {}, 利息约 {}".format(
                    _repayment_month_serial_number_data_lists['repayment_month_serial_number'][0],
                    _repayment_month_serial_number_data_lists['monthly_payment'][0],
                    _repayment_month_serial_number_data_lists['the_principal_has_be_repaid_during_the_month'][0],
                    _repayment_month_serial_number_data_lists['interest_is_due_during_the_month'][0],
                ),
                "\t  利息最低月为【第 {} 月】, 月供金额约: {}, 本金约 {}, 利息约 {}".format(
                    _repayment_month_serial_number_data_lists['repayment_month_serial_number'][-1],
                    _repayment_month_serial_number_data_lists['monthly_payment'][-1],
                    _repayment_month_serial_number_data_lists['the_principal_has_be_repaid_during_the_month'][-1],
                    _repayment_month_serial_number_data_lists['interest_is_due_during_the_month'][-1],
                ),
            ]

        message = '\n'.join(message_list)

        return message

    def main(self):
        print("还款方式: 等额本金")
        r1 = self.matching_the_principal_repayment()
        r1_msg = self._parse(r1)
        print(r1_msg)

        print("还款方式: 等额本息")
        r2 = self.equal_principal_and_interest_repayment()
        r2_msg = self._parse(r2)
        print(r2_msg)


def hacker_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--loan_amount",
        dest="loan_amount", action="store", type=float, required=True,
        help="贷款本金, 单位: 万"
    )
    parser.add_argument(
        "-t",
        "--loan_term",
        dest="loan_term", action="store", type=int, required=True,
        help="贷款年限"
    )
    parser.add_argument(
        "-r",
        "--interest_rate",
        dest="interest_rate", action="store", type=float, required=True,
        help="贷款年利率"
    )
    parser.add_argument(
        "-n",
        "--repayment_month_serial_number",
        dest="repayment_month_serial_number", action="store", type=int, required=False,
        default=60,
        help="还款月序号"
    )

    args = parser.parse_args()
    args_dict = vars(args)

    return args_dict


if __name__ == '__main__':
    args_dict = hacker_args()

    msc = MortgageSmartCalculator(**args_dict)
    msc.main()
