# End-to-end check. Server must be running on port 5000, data must be the clean 37-order set.
$base = "http://127.0.0.1:5000"
$fail = 0

function Check($name, $ok, $detail) {
  if ($ok) { "PASS  $name  ($detail)" }
  else { "FAIL  $name  ($detail)"; $script:fail++ }
}

# Count items in a JSON array response (works in PowerShell 5.1 and 7)
function CountOf($path) {
  $r = Invoke-RestMethod "$base$path"
  return $r.Count
}

$h = Invoke-RestMethod "$base/api/health"
Check "health" ($h.status -eq "ok" -and $h.database -eq "connected") "items=$($h.sale_items)"

$s = Invoke-RestMethod "$base/api/stats"
Check "stats orders"  ($s.total_orders -eq 37) $s.total_orders
Check "stats units"   ($s.total_units -eq 201) $s.total_units
Check "stats revenue" ([math]::Round($s.total_revenue,2) -eq 159188) $s.total_revenue

$m = Invoke-RestMethod "$base/api/charts/monthly-revenue"
$mSum = [math]::Round(($m.values | Measure-Object -Sum).Sum, 2)
Check "monthly chart" ($m.labels.Count -eq 10 -and $mSum -eq 159188) "labels=$($m.labels.Count) sum=$mSum"

$c = Invoke-RestMethod "$base/api/charts/category-sales"
$cSum = [math]::Round(($c.values | Measure-Object -Sum).Sum, 2)
Check "category chart" ($c.labels.Count -eq 5 -and $cSum -eq 159188) "labels=$($c.labels.Count) sum=$cSum"

$n = CountOf "/api/customers";  Check "customers"  ($n -eq 15) "got $n, expect 15"
$n = CountOf "/api/products";   Check "products"   ($n -eq 15) "got $n, expect 15"
$n = CountOf "/api/categories"; Check "categories" ($n -eq 5)  "got $n, expect 5"

$n = CountOf "/api/sales";                   Check "sales rows"        ($n -eq 69) "got $n, expect 69"
$n = CountOf "/api/sales?q=karan";           Check "search karan"      ($n -eq 6)  "got $n, expect 6"
$n = CountOf "/api/sales?category=Stationery"; Check "filter Stationery" ($n -eq 9)  "got $n, expect 9"

foreach ($path in "/", "/css/style.css", "/js/app.js") {
  $code = (Invoke-WebRequest "$base$path" -UseBasicParsing).StatusCode
  Check "page $path" ($code -eq 200) $code
}

if ($fail -eq 0) { "ALL CHECKS PASSED" } else { "$fail CHECK(S) FAILED" }