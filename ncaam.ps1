$webrequest = invoke-webrequest -Uri "https://www.espn.com/mens-college-basketball/teams"
while($index -lt 725){$string = ($webrequest.RawContent -split ('"u":"/mens-college-basketball/team/_/id/') -split('"n":"'))[$index]
 $id = [regex]::Match($string, '"id":"(\d+)"').Groups[1].Value
 $id >> ncaam.txt
 $index = $index + 2
}