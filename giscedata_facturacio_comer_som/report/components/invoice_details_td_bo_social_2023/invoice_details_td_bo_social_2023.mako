<%page args="bs" />
%if bs.is_visible:
<%
import locale
%>
<tr>
    <td class="td_first concepte_td">${_(u"Bo social")}</td>
    <td class="detall_td" colspan="${bs.number_of_columns}">${_(u"%s dies x %s €/dia") % (int(bs.days), locale.str(locale.atof(formatLang(bs.price_per_day, digits=6))))}</td>
    <td class="subtotal">${_(u"%s €") % formatLang(bs.subtotal)}</td>
</tr>
%endif