SELECT authorScopus.id AS authorCiting,   wr2.authorId AS authorCited, count(citesRelation.eidCited)
FROM authorScopus
INNER JOIN wroteRelation
  ON authorScopus.id = wroteRelation.authorId
INNER JOIN citesRelation
  ON wroteRelation.eid = citesRelation.eidCiting
INNER JOIN wroteRelation AS wr2
  ON citesRelation.eidCited = wr2.eid
WHERE 
  authorScopus.id = '6602571197' AND
  citesRelation.citationYear < 2019
 GROUP BY authorCited
ORDER BY authorCited
