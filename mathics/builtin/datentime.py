# -*- coding: utf-8 -*-

"""
Date and Time

Dates and times are represented symbolically; computations can be performed on them.

Date object can also input and output dates and times in a wide range of formats, as \
well as handle calendars.
"""

import re
import sys
import time
from datetime import datetime, timedelta
from typing import Optional, Union

import dateutil.parser

from mathics.core.atoms import Integer, MachineReal, Real, String
from mathics.core.attributes import (
    A_HOLD_ALL,
    A_NO_ATTRIBUTES,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import Builtin, Predefined
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.element import BaseElement, ImmutableValueMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import (
    SymbolAborted,
    SymbolAbsoluteTime,
    SymbolAutomatic,
    SymbolInfinity,
    SymbolRowBox,
)
from mathics.eval.datetime import eval_timeconstrained, valid_time_from_expression
from mathics.settings import TIME_12HOUR

START_TIME = time.time()

TIME_INCREMENTS = {
    "Year": (1, 0, 0, 0, 0, 0),
    "Quarter": (0, 3, 0, 0, 0, 0),
    "Month": (0, 1, 0, 0, 0, 0),
    "Week": (0, 0, 7, 0, 0, 0),
    "Day": (0, 0, 1, 0, 0, 0),
    "Hour": (0, 0, 0, 1, 0, 0),
    "Minute": (0, 0, 0, 0, 1, 0),
    "Second": (0, 0, 0, 0, 0, 1),
}

# FIXME: Some of the formats are not supported by strftime/strptime
# (commented out)
DATE_STRING_FORMATS = {
    "Date": "%c",
    "DateShort": "%a %d %b %Y",
    "Time": "%X",
    "DateTime": "%c %X",
    "DateTimeShort": "%a %d %b %Y %X",
    "Year": "%Y",
    "YearShort": "%y",
    # "QuarterName": "Quarter N",
    # "QuarterNameShort": "QN",
    # "Quarter": "",
    "MonthName": "%B",
    "MonthNameShort": "%b",
    # "MonthNameInitial": "%b",
    "Month": "%m",
    "MonthShort": "%m",
    "DayName": "%A",
    "DayNameShort": "%a",
    # "DayNameInitial": "%a",
    "Day": "%d",
    "DayShort": "%d",
    "Hour": "%I" if TIME_12HOUR else "%H",
    "Hour12": "%I",
    "Hour24": "%H",
    "HourShort": "%H",
    "Hour12Short": "%I",
    "Hour24Short": "%H",
    "AMPM": "%p",
    # "AMPMLowerCase": "%p",
    "Minute": "%M",
    "MinuteShort": "%M",
    "Second": "%S",
    "SecondShort": "%S",
    "SecondExact": "%S.%f",
    # "Millisecond": "%f",
    # "MillisecondShort": "",
}

EPOCH_START = datetime(1900, 1, 1)

total_seconds = timedelta.total_seconds

SymbolDateObject = Symbol("DateObject")
SymbolDateString = Symbol("DateString")
SymbolGregorian = Symbol("Gregorian")


class _Date:
    def __init__(
        self, datelist_arg: Union[list, tuple] = [], absolute=None, datestr=None
    ):
        datelist = list(datelist_arg) + [1900, 1, 1, 0, 0, 0.0][len(datelist_arg) :]
        self.date = datetime(
            datelist[0],
            datelist[1],
            datelist[2],
            datelist[3],
            datelist[4],
            int(datelist[5]),
            int(1e6 * (datelist[5] % 1.0)),
        )
        if absolute is not None:
            self.date += timedelta(seconds=absolute)
        if datestr is not None:
            if absolute is not None:
                raise ValueError
            self.date = dateutil.parser.parse(datestr)

    def addself(self, timevec: tuple):
        years = self.date.year + timevec[0] + int((self.date.month + timevec[1]) / 12)
        months = (self.date.month + timevec[1]) % 12
        if months == 0:
            months += 12
            years -= 1
        self.date = datetime(
            years,
            months,
            self.date.day,
            self.date.hour,
            self.date.minute,
            self.date.second,
        )
        tdelta = timedelta(
            days=timevec[2], hours=timevec[3], minutes=timevec[4], seconds=timevec[5]
        )
        self.date += tdelta

    def to_list(self) -> list:
        return [
            self.date.year,
            self.date.month,
            self.date.day,
            self.date.hour,
            self.date.minute,
            self.date.second + 1e-6 * self.date.microsecond,
        ]


class _DateFormat(Builtin):
    messages = {
        "arg": "Argument `1` cannot be interpreted as a date or time input.",
        "str": "String `1` cannot be interpreted as a date in format `2`.",
        "ambig": "The interpretation of `1` is ambiguous.",
        "fmt": "`1` is not a valid date format.",
    }

    automatic = re.compile(
        r"^([0-9]{1,4})\s*([^0-9]*)\s*([0-9]{1,2})\s*\2\s*([0-9]{1,4})\s*"
    )

    def parse_date_automatic(self, epochtime, etime, evaluation: Evaluation):
        m = _DateFormat.automatic.search(etime)
        if not m:
            return dateutil.parser.parse(etime)

        x1, x2, x3 = tuple(m.group(i) for i in (1, 3, 4))
        i1, i2, i3 = tuple(int(x) for x in (x1, x2, x3))

        if len(x1) <= 2:
            if i1 > 12:
                month_day = "%d %m"
                is_ambiguous = False
            else:
                month_day = "%m %d"
                is_ambiguous = not (i2 > 12 or i1 == i2)  # is i2 not clearly a day?

            if len(x3) <= 2:
                date = datetime.strptime(
                    "%02d %02d %02d" % (i1, i2, i3), month_day + " %y"
                )
            else:
                date = datetime.strptime(
                    "%02d %02d %04d" % (i1, i2, i3), month_day + " %Y"
                )
        elif len(x1) == 4:
            is_ambiguous = False
            date = datetime.strptime("%04d %02d %02d" % (i1, i2, i3), "%Y %m %d")
        else:
            raise ValueError()

        date = dateutil.parser.parse(
            datetime.strftime(date, "%x") + " " + etime[len(m.group(0)) :]
        )

        if is_ambiguous:
            evaluation.message(self.get_name(), "ambig", epochtime)

        return date

    def to_datelist(self, epochtime, evaluation: Evaluation):
        """Converts date-time 'epochtime' to datelist"""
        etime = epochtime.to_python()

        form_name = self.get_name()

        if isinstance(etime, float) or isinstance(etime, int):
            date = EPOCH_START + timedelta(seconds=etime)
            datelist = [
                date.year,
                date.month,
                date.day,
                date.hour,
                date.minute,
                date.second + 1e-06 * date.microsecond,
            ]
            return datelist

        if isinstance(etime, str):
            try:
                date = self.parse_date_automatic(
                    epochtime, etime.strip('"'), evaluation
                )
            except ValueError:
                evaluation.message(form_name, "str", epochtime, "Automatic")
                return
            datelist = [
                date.year,
                date.month,
                date.day,
                date.hour,
                date.minute,
                date.second + 1e-06 * date.microsecond,
            ]
            return datelist

        if not isinstance(etime, (list, tuple)):
            evaluation.message(form_name, "arg", etime)
            return

        if 1 <= len(etime) <= 6 and all(  # noqa
            (isinstance(val, float) and i > 1) or isinstance(val, int)
            for i, val in enumerate(etime)
        ):
            default_date = [1900, 1, 1, 0, 0, 0.0]
            datelist = list(etime) + default_date[len(etime) :]
            prec_part, imprec_part = datelist[:2], datelist[2:]

            try:
                dtime = datetime(prec_part[0], prec_part[1], 1)
            except ValueError:
                # FIXME datetime is fairly easy to overflow. 1 <= month <= 12
                # and some bounds on year too.
                evaluation.message(form_name, "arg", epochtime)
                return

            tdelta = timedelta(
                days=imprec_part[0] - 1,
                hours=imprec_part[1],
                minutes=imprec_part[2],
                seconds=imprec_part[3],
            )
            dtime += tdelta
            datelist = [
                dtime.year,
                dtime.month,
                dtime.day,
                dtime.hour,
                dtime.minute,
                dtime.second + 1e-06 * dtime.microsecond,
            ]
            return datelist

        if len(etime) == 2:
            if (
                isinstance(etime[0], str)
                and isinstance(etime[1], (list, tuple))  # noqa
                and all(isinstance(s, str) for s in etime[1])
            ):
                is_spec = [
                    str(s).strip('"') in DATE_STRING_FORMATS.keys() for s in etime[1]
                ]

                if isinstance(etime, tuple):
                    etime = list(etime)

                etime[1] = [str(s).strip('"') for s in etime[1]]

                if sum(is_spec) == len(is_spec):
                    forms = []
                    fields = [DATE_STRING_FORMATS[s] for s in etime[1]]
                    for sep in ["", " ", "/", "-", ".", ",", ":"]:
                        forms.append(sep.join(fields))
                else:
                    forms = [""]
                    for i, s in enumerate(etime[1]):
                        if is_spec[i]:
                            forms[0] += DATE_STRING_FORMATS[s]
                        else:
                            # TODO: Escape % signs?
                            forms[0] += s

                date = _Date()
                date.date = None
                for form in forms:
                    try:
                        date.date = datetime.strptime(str(etime[0]).strip('"'), form)
                        break
                    except ValueError:
                        pass

                if date.date is None:
                    evaluation.message(form_name, "str", etime[0], etime[1])
                    return
                datelist = date.to_list()

                # If year is ambiguous, assume the current year
                if "Year" not in etime[1] and "YearShort" not in etime[1]:
                    datelist[0] = datetime.today().year

                return datelist

            else:
                evaluation.message(form_name, "str", etime[0], etime[1])
                return

        evaluation.message(form_name, "arg", epochtime)
        return


class AbsoluteTime(_DateFormat):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/AbsoluteTime.html</url>

    <dl>
      <dt>'AbsoluteTime[]'
      <dd>gives the local time in seconds since epoch January 1, 1900, in your \
          time zone.

      <dt>'AbsoluteTime'[{$y$, $m$, $d$, $h$, $m$, $s$}]
      <dd>gives the absolute time specification corresponding to a date list.

      <dt>'AbsoluteTime'["$string$"]
      <dd>gives the absolute time specification for a given date string.

      <dt>'AbsoluteTime'[{"$string$",{$e_1$, $e_2$, ...}}]
      <dd>takgs the date string to contain the elements "$ei$".
    </dl>

    >> AbsoluteTime[]
     = ...

    >> AbsoluteTime[{2000}]
     = 3155673600

    >> AbsoluteTime[{"01/02/03", {"Day", "Month", "YearShort"}}]
     = 3253046400

    >> AbsoluteTime["6 June 1991"]
     = 2885155200

    >> AbsoluteTime[{"6-6-91", {"Day", "Month", "YearShort"}}]
     = 2885155200
    """

    summary_text = "get absolute time in seconds"

    def eval_now(self, evaluation: Evaluation) -> MachineReal:
        "AbsoluteTime[]"

        return Real(total_seconds(datetime.now() - EPOCH_START))

    def eval_spec(self, epochtime, evaluation: Evaluation) -> Optional[MachineReal]:
        "AbsoluteTime[epochtime_]"

        datelist = self.to_datelist(epochtime, evaluation)

        if datelist is None:
            return

        date = _Date(datelist_arg=datelist)
        tdelta = date.date - EPOCH_START
        if tdelta.microseconds == 0:
            return Integer(int(total_seconds(tdelta)))
        return Real(total_seconds(tdelta))


class AbsoluteTiming(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/AbsoluteTiming.html</url>

    <dl>
      <dt>'AbsoluteTiming'[$expr$]
      <dd>evaluates $expr$, returning a list of the absolute number of seconds in \
          real time that have elapsed, together with the result obtained.
    </dl>

    >> AbsoluteTiming[50!]
     = {..., 30414093201713378043612608166064768844377641568960512000000000000}
    >> Attributes[AbsoluteTiming]
     = {HoldAll, Protected}
    """

    attributes = A_HOLD_ALL | A_PROTECTED

    summary_text = "get total wall-clock time to run a Mathics command"

    def eval(self, expr: BaseElement, evaluation: Evaluation) -> ListExpression:
        "AbsoluteTiming[expr_]"

        start = time.time()
        result = expr.evaluate(evaluation)
        stop = time.time()
        return ListExpression(Real(stop - start), result)


class DateDifference(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/DateDifference.html</url>

    <dl>
      <dt>'DateDifference'[$date_1$, $date_2$]
      <dd>returns the difference between $date_1$ and $date_2$ in days.

      <dt>'DateDifference'[$date_1$, $date_2$, $unit$]
      <dd>returns the difference in the specified $unit$.

      <dt>'DateDifference'[$date_1$, $date_2$, {$unit_1$, $unit_2$, ...}]
      <dd>represents the difference as a list of integer multiples of each $unit$, with any remainder expressed in the smallest unit.
    </dl>

    >> DateDifference[{2042, 1, 4}, {2057, 1, 1}]
     = 5476

    >> DateDifference[{1936, 8, 14}, {2000, 12, 1}, "Year"]
     = {64.3425, Year}

    >> DateDifference[{2010, 6, 1}, {2015, 1, 1}, "Hour"]
     = {40200, Hour}

    >> DateDifference[{2003, 8, 11}, {2003, 10, 19}, {"Week", "Day"}]
     = {{9, Week}, {6, Day}}
    """

    # FIXME: Since timedelta does not use large time units (years, months etc)
    # this method can be inaccurate. The example below gives fractional Days
    # (20.1666666667 not 20).

    """
    >> DateDifference[{2000, 6, 15}, {2001, 9, 4}, {"Month", "Day"}]
     = {{14, "Month"}, {20, "Day"}}
    """

    attributes = A_READ_PROTECTED | A_PROTECTED

    messages = {
        "date": "Argument `1` cannot be interpreted as a date.",
        "inc": (
            "Argument `1` is not a time increment or " "a list of time increments."
        ),
    }

    rules = {"DateDifference[date1_, date2_]": 'DateDifference[date1, date2, "Day"]'}

    summary_text = "find the difference in days, weeks, etc. between two dates"

    def eval(
        self,
        date1: BaseElement,
        date2: BaseElement,
        units: BaseElement,
        evaluation: Evaluation,
    ) -> Optional[BaseElement]:
        "DateDifference[date1_, date2_, units_]"

        # Process dates
        pydate1, pydate2 = date1.to_python(), date2.to_python()

        if isinstance(pydate1, (list, tuple)):  # Date List
            idate = _Date(datelist_arg=pydate1)
        elif isinstance(pydate1, (float, int)):  # Absolute Time
            idate = _Date(absolute=pydate1)
        elif isinstance(pydate1, str):  # Date string
            idate = _Date(datestr=pydate2.strip('"'))
        else:
            evaluation.message("DateDifference", "date", date1)
            return

        if isinstance(pydate2, (list, tuple)):  # Date List
            fdate = _Date(datelist_arg=pydate2)
        elif isinstance(pydate2, (int, float)):  # Absolute Time
            fdate = _Date(absolute=pydate2)
        elif isinstance(pydate1, str):  # Date string
            fdate = _Date(datestr=pydate2.strip('"'))
        else:
            evaluation.message("DateDifference", "date", date2)
            return

        try:
            tdelta = fdate.date - idate.date
        except OverflowError:
            evaluation.message("General", "ovf")
            return

        # Process Units
        pyunits = units.to_python()
        if isinstance(pyunits, str):
            pyunits = [str(pyunits.strip('"'))]
        elif isinstance(pyunits, (list, tuple)) and all(
            isinstance(p, str) for p in pyunits
        ):
            pyunits = [p.strip('"') for p in pyunits]

        if not all(p in TIME_INCREMENTS.keys() for p in pyunits):
            evaluation.message("DateDifference", "inc", units)

        def intdiv(a, b, flag=True):
            "exact integer division where possible"
            if flag:
                if a % b == 0:
                    return a // b
                else:
                    return a / b
            else:
                return a // b

        if not isinstance(pyunits, list):
            pyunits = [pyunits]

        # Why doesn't this work?
        # pyunits = pyunits.sort(key=TIME_INCREMENTS.get, reverse=True)

        pyunits = [(a, TIME_INCREMENTS.get(a)) for a in pyunits]
        pyunits.sort(key=lambda a: a[1], reverse=True)
        pyunits = [a[0] for a in pyunits]

        seconds = int(total_seconds(tdelta))

        result = []
        flag = False
        for i, unit in enumerate(pyunits):
            if i + 1 == len(pyunits):
                flag = True

            if unit == "Year":
                result.append([intdiv(seconds, 365 * 24 * 60 * 60, flag), "Year"])
                seconds = seconds % (365 * 24 * 60 * 60)
            if unit == "Quarter":
                result.append([intdiv(seconds, 365 * 6 * 60 * 60, flag), "Quarter"])
                seconds = seconds % (365 * 6 * 60 * 60)
            if unit == "Month":
                result.append([intdiv(seconds, 365 * 2 * 60 * 60, flag), "Month"])
                seconds = seconds % (365 * 2 * 60 * 60)
            if unit == "Week":
                result.append([intdiv(seconds, 7 * 24 * 60 * 60, flag), "Week"])
                seconds = seconds % (7 * 24 * 60 * 60)
            if unit == "Day":
                result.append([intdiv(seconds, 24 * 60 * 60, flag), "Day"])
                seconds = seconds % (24 * 60 * 60)
            if unit == "Hour":
                result.append([intdiv(seconds, 60 * 60, flag), "Hour"])
                seconds = seconds % (60 * 60)
            if unit == "Minute":
                result.append([intdiv(seconds, 60, flag), "Minute"])
                seconds = seconds % 60
            if unit == "Second":
                result.append(
                    [intdiv(seconds + total_seconds(tdelta) % 1, 1, flag), "Second"]
                )

        if len(result) == 1:
            if pyunits[0] == "Day":
                return Integer(result[0][0])
            return from_python(result[0])
        return from_python(result)


class DateObject(_DateFormat, ImmutableValueMixin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/DateObject.html</url>

    <dl>
      <dt>'DateObject[...]'
      <dd> Returns an object codifying DateList....
    </dl>

    >> DateObject[{2020, 4, 15}]
     = [...]
    """

    fmt_keywords = {
        "Year": 0,
        "Month": 1,
        "Day": 2,
        "Hour": 3,
        "Minute": 4,
        "Second": 5,
    }

    granularities = [
        Symbol(s)
        for s in ["Eternity", "Year", "Month", "Day", "Hour", "Minute", "Instant"]
    ]

    messages = {
        "notz": (
            "Argument `1` in DateObject is not a recognized " "TimeZone specification."
        ),
    }

    options = {
        "TimeZone": "Automatic",
        "CalendarType": "Automatic",
        "DateFormat": "Automatic",
    }

    rules = {
        "DateObject[]": "DateObject[AbsoluteTime[]]",
    }

    summary_text = "get an object representing a date (year, hour, instant, ...)"

    def eval_any(
        self, args: BaseElement, evaluation: Evaluation, options: dict
    ) -> Optional[Expression]:
        "DateObject[args_, OptionsPattern[]]"
        datelist = None
        tz = None
        if isinstance(args, Expression):
            if args.get_head_name() in ("System`Rule", "System`DelayedRule"):
                options[args.elements[0].get_name()] = args.elements[1]
                args = Expression(SymbolAbsoluteTime).evaluate(evaluation)
            elif args.get_head_name() == "System`DateObject":
                datelist = args._elements[0]
                tz = args._elements[3]

        if datelist is None:
            datelist = self.to_datelist(args, evaluation)
            tz = Real(-time.timezone / 3600.0)
        if datelist is None:
            return

        fmt = None

        if options["System`TimeZone"].sameQ(SymbolAutomatic):
            timezone = Real(-time.timezone / 3600.0)
        else:
            timezone = options["System`TimeZone"].evaluate(evaluation)
            if not timezone.is_numeric(evaluation):
                evaluation.message("DateObject", "notz", timezone)

        # TODO: if tz != timezone, shift the datetime list.
        if not tz == timezone:
            dt = timezone.to_python() - tz.to_python()
            if len(datelist) > 3:
                newhour = datelist[3] + dt
                datelist = datelist[:3] + [newhour] + datelist[4:]

        epoch = Symbol("Eternity")
        if datelist[-1] == 0:
            for i in range(len(datelist)):
                if datelist[-1 - i] != 0:
                    datelist = datelist[:-i]
                    epoch = self.granularities[-i - 1]
                    break
        else:
            epoch = Symbol("Instant")

        fmt = options["System`DateFormat"]
        if len(datelist) < 6:
            datelist = [Integer(d) for d in datelist]
        else:
            datelist = [Integer(d) for d in datelist[:5]] + [Real(datelist[5])]
        return to_expression(
            SymbolDateObject,
            datelist,
            epoch,
            SymbolGregorian,
            timezone,
            fmt,
        )

    def eval_makeboxes(
        self,
        datetime: Expression,
        gran: BaseElement,
        cal: BaseElement,
        tz: BaseElement,
        fmt: BaseElement,
        evaluation: Evaluation,
    ) -> Optional[Expression]:
        "MakeBoxes[DateObject[datetime_List, gran_, cal_, tz_, fmt_], StandardForm|TraditionalForm|OutputForm]"
        # TODO:
        if fmt.sameQ(SymbolAutomatic):
            fmt = ListExpression(String("DateTimeShort"))
        fmtds = Expression(SymbolDateString, datetime, fmt).evaluate(evaluation)
        if fmtds is None:
            return
        # tz_string = to_mathic_expression("ToString", tz).evaluate(evaluation)
        tz_string = String(str(int(tz.to_python())))
        return to_expression(
            SymbolRowBox, to_mathics_list("[", fmtds, "  GTM", tz_string, "]")
        )


class DatePlus(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/DatePlus.html</url>

    <dl>
      <dt>'DatePlus'[$date$, $n$]
      <dd>finds the date $n$ days after $date$.

      <dt>'DatePlus'[$date$, {$n$, "$unit$"}]
      <dd>finds the date $n$ units after $date$.

      <dt>'DatePlus'[$date$, {{$n_1$, "$unit_1$"}, {$n_2$, "$unit_2$"}, ...}]
      <dd>finds the date which is $n_i$ specified units after $date$.

      <dt>'DatePlus'[$n$]
      <dd>finds the date $n$ days after the current date.

      <dt>'DatePlus'[$offset$]
      <dd>finds the date which is offset from the current date.
    </dl>

    Add 73 days to Feb 5, 2010:
    >> DatePlus[{2010, 2, 5}, 73]
     = {2010, 4, 19}

    Add 8 weeks and 1 day to March 16, 1999:
    >> DatePlus[{2010, 2, 5}, {{8, "Week"}, {1, "Day"}}]
     = {2010, 4, 3}
    """

    attributes = A_READ_PROTECTED | A_PROTECTED

    messages = {
        "date": "Argument `1` cannot be interpreted as a date.",
        "inc": (
            "Argument `1` is not a time increment or a list " "of time increments."
        ),
    }

    rules = {"DatePlus[n_]": "DatePlus[Take[DateList[], 3], n]"}

    summary_text = "add or subtract days, weeks, etc. in a date list or string"

    def eval(
        self, date: BaseElement, off: BaseElement, evaluation: Evaluation
    ) -> Optional[Expression]:
        "DatePlus[date_, off_]"

        # Process date
        pydate = date.to_python()
        if isinstance(pydate, (list, tuple)):
            date_prec = len(pydate)
            idate = _Date(datelist_arg=pydate)
        elif isinstance(pydate, float) or isinstance(pydate, int):
            date_prec = "absolute"
            idate = _Date(absolute=pydate)
        elif isinstance(pydate, str):
            date_prec = "string"
            idate = _Date(datestr=pydate.strip('"'))
        else:
            evaluation.message("DatePlus", "date", date)
            return

        # Process offset
        pyoff = off.to_python()
        if isinstance(pyoff, float) or isinstance(pyoff, int):
            pyoff = [[pyoff, '"Day"']]
        elif (
            isinstance(pyoff, (list, tuple))
            and len(pyoff) == 2
            and isinstance(pyoff[1], str)
        ):
            pyoff = [pyoff]

        # Strip " marks
        pyoff = [[x[0], x[1].strip('"')] for x in pyoff]

        if isinstance(pyoff, (list, tuple)) and all(  # noqa
            len(o) == 2
            and o[1] in TIME_INCREMENTS.keys()
            and isinstance(o[0], (float, int))
            for o in pyoff
        ):
            for o in pyoff:
                idate.addself([o[0] * TIME_INCREMENTS[o[1]][i] for i in range(6)])
        else:
            evaluation.message("DatePlus", "inc", off)
            return

        if isinstance(date_prec, int):
            result = to_mathics_list(
                *idate.to_list()[:date_prec], elements_conversion_fn=Integer
            )
        elif date_prec == "absolute":
            result = Expression(SymbolAbsoluteTime, idate.to_list())
        elif date_prec == "string":
            result = Expression(
                SymbolDateString,
                to_mathics_list(*idate.to_list(), elements_conversion_fn=Integer),
            )

        return result


class DateList(_DateFormat):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/DateList.html</url>

    <dl>
      <dt>'DateList[]'
      <dd>returns the current local time in the form {$year$, $month$, $day$, $hour$, $minute$, $second$}.

      <dt>'DateList'[$time$]
      <dd>returns a formatted date for the number of seconds $time$ since epoch Jan 1 1900.

      <dt>'DateList'[{$y$, $m$, $d$, $h$, $m$, $s$}]
      <dd>converts an incomplete date list to the standard representation.
    </dl>

    >> DateList[0]
     = {1900, 1, 1, 0, 0, 0.}

    >> DateList[3155673600]
     = {2000, 1, 1, 0, 0, 0.}

    >> DateList[{2003, 5, 0.5, 0.1, 0.767}]
     = {2003, 4, 30, 12, 6, 46.02}

    >> DateList[{2012, 1, 300., 10}]
     = {2012, 10, 26, 10, 0, 0.}

    >> DateList["31/10/1991"]
     = {1991, 10, 31, 0, 0, 0.}

    >> DateList["1/10/1991"]
     : The interpretation of 1/10/1991 is ambiguous.
     = {1991, 1, 10, 0, 0, 0.}

    >> DateList[{"31/10/91", {"Day", "Month", "YearShort"}}]
     = {1991, 10, 31, 0, 0, 0.}

    >> DateList[{"31 10/91", {"Day", " ", "Month", "/", "YearShort"}}]
     = {1991, 10, 31, 0, 0, 0.}


    If not specified, the current year assumed
    >> DateList[{"5/18", {"Month", "Day"}}]
     = {..., 5, 18, 0, 0, 0.}
    """

    # TODO: Somehow check that the current year is correct

    rules = {
        "DateList[]": "DateList[AbsoluteTime[]]",
        'DateList["02/27/20/13"]': 'Import[Uncompress["eJxTyigpKSi20tfPzE0v1qvITk7RS87P1QfizORi/czi/HgLMwNDvYK8dCUATpsOzQ=="]]',
    }

    summary_text = "date elements as numbers in {y,m,d,h,m,s} format"

    def eval(
        self, epochtime: BaseElement, evaluation: Evaluation
    ) -> Optional[ListExpression]:
        "%(name)s[epochtime_]"
        datelist = self.to_datelist(epochtime, evaluation)

        if datelist is None:
            return

        date_elements = [Integer(i) for i in datelist[:-1]] + [Real(datelist[-1])]
        return ListExpression(*date_elements)


class DateString(_DateFormat):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/DateString.html</url>

    <dl>
      <dt>'DateString[]'
      <dd>returns the current local time and date as a string.

      <dt>'DateString'[$elem$]
      <dd>returns the time formatted according to $elems$.

      <dt>'DateString'[{$e_1$, $e_2$, ...}]
      <dd>concatenates the time formatted according to elements $ei$.

      <dt>'DateString'[$time$]
      <dd>returns the date string of an AbsoluteTime.

      <dt>'DateString'[{$y$, $m$, $d$, $h$, $m$, $s$}]
      <dd>returns the date string of a date list specification.

      <dt>'DateString'[$string$]
      <dd>returns the formatted date string of a date string specification.

      <dt>'DateString'[$spec$, $elems$]
      <dd>formats the time in turns of $elems$. Both $spec$ and $elems$ can take any of the above formats.
    </dl>

    The current date and time:
    >> DateString[];

    >> DateString[{1991, 10, 31, 0, 0}, {"Day", " ", "MonthName", " ", "Year"}]
     = 31 October 1991

    >> DateString[{2007, 4, 15, 0}]
     = Sun 15 Apr 2007 00:00:00

    >> DateString[{1979, 3, 14}, {"DayName", "  ", "Month", "-", "YearShort"}]
     = Wednesday  03-79

    Non-integer values are accepted too:
    >> DateString[{1991, 6, 6.5}]
     = Thu 6 Jun 1991 12:00:00
    """

    attributes = A_READ_PROTECTED | A_PROTECTED

    rules = {
        "DateString[]": "DateString[DateList[], $DateStringFormat]",
        "DateString[format_?(VectorQ[#1, StringQ]&)]": (
            "DateString[DateList[], format]"
        ),
        "DateString[epochtime_]": "DateString[epochtime, $DateStringFormat]",
    }

    summary_text = "current or specified date as a string in many possible formats"

    def eval(
        self, epochtime: BaseElement, form: BaseElement, evaluation: Evaluation
    ) -> Optional[String]:
        "DateString[epochtime_, form_]"

        datelist = self.to_datelist(epochtime, evaluation)

        if datelist is None:
            return

        date = _Date(datelist_arg=datelist)

        pyform = form.to_python()
        if not isinstance(pyform, (list, tuple)):
            pyform = [pyform]

        pyform = [x.strip('"') for x in pyform]

        if not all(isinstance(f, str) for f in pyform):
            evaluation.message("DateString", "fmt", form)
            return

        datestrs = []
        for p in pyform:
            if str(p) in DATE_STRING_FORMATS.keys():
                # FIXME: Years 1900 before raise an error
                tmp = date.date.strftime(DATE_STRING_FORMATS[p])
                if str(p).endswith("Short") and str(p) != "YearShort":
                    if str(p) == "DateTimeShort":
                        tmp = tmp.split(" ")
                        tmp = " ".join([s.lstrip("0") for s in tmp[:-1]] + [tmp[-1]])
                    else:
                        tmp = " ".join([s.lstrip("0") for s in tmp.split(" ")])
            else:
                tmp = str(p)

            datestrs.append(tmp)

        return String("".join(datestrs))


class DateStringFormat(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/$DateStringFormat.html</url>

    <dl>
      <dt>'\$DateStringFormat'
      <dd>gives the format used for dates generated by 'DateString'.
    </dl>

    >> $DateStringFormat
     = {DateTimeShort}
    """

    name = "$DateStringFormat"

    value = "DateTimeShort"

    summary_text = "get default date string format as a list"

    # TODO: Methods to change this

    def evaluate(self, evaluation: Evaluation) -> ListExpression:
        return ListExpression(String(self.value))


class EasterSunday(Builtin):  # Calendar`EasterSunday
    """
    <url>:Date of Easter:
    https://en.wikipedia.org/wiki/Date_of_Easter</url> (<url>
    :WMA link:
    https://reference.wolfram.com/language/Calendar/ref/EasterSunday.html</url>)

    <dl>
      <dt>'EasterSunday'[$year$]
      <dd>returns the date of the Gregorian Easter Sunday as {year, month, day}.
    </dl>

    >> EasterSunday[2000]
     = {2000, 4, 23}

    >> EasterSunday[2030]
     = {2030, 4, 21}
    """

    summary_text = "find the date of Easter Sunday for a given year"

    def eval(self, year: Integer, evaluation: Evaluation) -> ListExpression:
        "EasterSunday[year_Integer]"
        y = year.value

        # "Anonymous Gregorian algorithm", see https://en.wikipedia.org/wiki/Computus
        a = y % 19
        b = y // 100
        c = y % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        le = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * le) // 451
        month = (h + le - 7 * m + 114) // 31
        day = ((h + le - 7 * m + 114) % 31) + 1

        return ListExpression(year, Integer(month), Integer(day))


class SystemTimeZone(Predefined):
    r"""
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/$SystemTimeZone.html</url>

    <dl>
      <dt>'\$SystemTimeZone'
      <dd> gives the current time zone for the computer system on which Mathics is \
           being run.
    </dl>

    >> $SystemTimeZone
     = ...
    """

    name = "$SystemTimeZone"
    value = Real(-time.timezone / 3600.0)

    summary_text = "get the time zone used by your system"

    def evaluate(self, evaluation: Evaluation) -> MachineReal:
        return self.value


class Now(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Now.html</url>

    <dl>
      <dt>'Now'
      <dd> gives the current time on the system.
    </dl>

    >> Now
     = ...
    """

    summary_text = "get current date and time"

    def evaluate(self, evaluation: Evaluation) -> Expression:
        return Expression(SymbolDateObject.evaluate(evaluation))


class TimeConstrained(Builtin):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/TimeConstrained.html</url>

    <dl>
      <dt>'TimeConstrained'[$expr$, $t$]
      <dd>'evaluates $expr$, stopping after $t$ seconds.'

      <dt>'TimeConstrained'[$expr$, $t$, $failexpr$]
      <dd>'returns $failexpr$ if the time constraint is not met.'
    </dl>

    Possible issues: for certain time-consuming functions (like simplify)
    which are based on sympy or other libraries, it is possible that
    the evaluation continues after the timeout. However, at the end of the \
    evaluation, the function will return '\$Aborted' and the results will not affect
    the state of the Mathics3 kernel.


    ## >> TimeConstrained[Pause[5]; a, 1]
    ##  = $Aborted

    ## 'TimeConstrained' can be nested. In this case, the outer 'TimeConstrained' waits for \
    ## 2 seconds that the inner sequence be executed. Inner expressions would take in \
    ## sequence more than 3 seconds:
    ## >> TimeConstrained[TimeConstrained[Pause[1]; Print["First Done"], 2];\
    ##              TimeConstrained[Pause[5];Print["Second Done"],2,"inner"], \
    ##              2, "outer"]
    ## | First Done
    ## = outer
    """

    attributes = A_HOLD_ALL | A_PROTECTED
    messages = {
        "timc": (
            "Number of seconds `1` is not a positive machine-sized number "
            "or Infinity."
        ),
    }
    if sys.platform == "emscripten":
        messages.update({"tcns": f"TimeConstrained is not supported in {sys.platform}"})

    summary_text = "run a command for at most a specified time"

    def eval_with_timeout(self, expr, t, evaluation) -> Optional[BaseElement]:
        "TimeConstrained[expr_, t_]"
        try:
            timeout = valid_time_from_expression(t, evaluation)
        except ValueError:
            evaluation.message("TimeConstrained", "timc", t)
            return
        return eval_timeconstrained(expr, timeout, SymbolAborted, evaluation)

    def eval_with_timeout_and_failexpr(
        self, expr, t, failexpr, evaluation
    ) -> Optional[BaseElement]:
        "TimeConstrained[expr_, t_, failexpr_]"
        try:
            timeout = valid_time_from_expression(t, evaluation)
        except ValueError:
            evaluation.message("TimeConstrained", "timc", t)
            return
        return eval_timeconstrained(expr, timeout, failexpr, evaluation)


class TimeZone(Predefined):
    r"""
    <url>:Time Zone:https://en.wikipedia.org/wiki/Time_zone</url> (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/$TimeZone.html</url>)

    <dl>
      <dt>'\$TimeZone'
      <dd> gives the current time zone to assume for dates and times.
    </dl>

    >> $TimeZone
     = ...
    """

    attributes = A_NO_ATTRIBUTES
    name = "$TimeZone"
    value = SystemTimeZone.value.copy()

    rules = {
        "$TimeZone": str(value),
    }

    summary_text = "gets the default time zone"

    def evaluate(self, evaluation: Evaluation) -> MachineReal:
        return self.value


class TimeUsed(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/TimeUsed.html</url>

    <dl>
    <dt>'TimeUsed[]'
      <dd>returns the total CPU time used for this session, in seconds.
      </dl>

    >> TimeUsed[]
     = ...
    """

    summary_text = (
        "get the total number of seconds of CPU time in the current Mathics3 session"
    )

    def eval(self, evaluation: Evaluation) -> MachineReal:
        "TimeUsed[]"
        # time.process_time() is better than
        # time.clock(). See https://bugs.python.org/issue31803
        return Real(time.process_time())


class Timing(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Timing.html</url>

    <dl>
      <dt>'Timing'[$expr$]
      <dd>measures the processor time taken to evaluate $expr$.
          It returns a list containing the measured time in seconds and \
          the result of the evaluation.
    </dl>

    >> Timing[50!]
     = {..., 30414093201713378043612608166064768844377641568960512000000000000}
    >> Attributes[Timing]
     = {HoldAll, Protected}
    """

    attributes = A_HOLD_ALL | A_PROTECTED

    summary_text = "get CPU time to run a Mathics3 command"

    def eval(self, expr: BaseElement, evaluation: Evaluation) -> ListExpression:
        "Timing[expr_]"

        start = time.process_time()
        result = expr.evaluate(evaluation)
        stop = time.process_time()
        return ListExpression(Real(stop - start), result)


class SessionTime(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SessionTime.html</url>

    <dl>
      <dt>'SessionTime[]'
      <dd>returns the total time in seconds since this session started.
    </dl>

    >> SessionTime[]
     = ...
    """

    summary_text = (
        "get total elapsed time in seconds since the beginning of Mathics3 session"
    )

    def eval(self, evaluation: Evaluation) -> MachineReal:
        "SessionTime[]"
        return Real(time.time() - START_TIME)


class TimeRemaining(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/TimeRemaining.html</url>

    <dl>
      <dt>'TimeRemaining[]'
      <dd>Gives the number of seconds remaining until the earliest enclosing \
          'TimeConstrained' will request the current computation to stop.

      <dt>'TimeConstrained'[$expr$, $t$, $failexpr$]
      <dd>returns $failexpr$ if the time constraint is not met.
    </dl>

    If TimeConstrained is called out of a TimeConstrained expression, returns 'Infinity':
    >> TimeRemaining[]
     = Infinity

    X> TimeConstrained[1+2; Print[TimeRemaining[]], 0.9]
     | 0.899318

    """

    summary_text = "get remaining time in allowed to run an expression"

    def eval(self, evaluation: Evaluation) -> BaseElement:
        "TimeRemaining[]"
        if len(evaluation.timeout_queue) > 0:
            t, start_time = evaluation.timeout_queue[-1]
            curr_time = datetime.now().timestamp()
            deltat = t + start_time - curr_time
            return Real(deltat)
        else:
            return SymbolInfinity
