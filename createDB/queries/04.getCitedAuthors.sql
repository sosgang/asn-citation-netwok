SELECT authorScopus.id AS authorCiting,  wroteRelation.eid  AS eidCiting,  citesRelation.eidCited, wr2.authorId AS authorCited
FROM authorScopus
INNER JOIN wroteRelation
  ON authorScopus.id = wroteRelation.authorId
INNER JOIN citesRelation
  ON wroteRelation.eid = citesRelation.eidCiting
INNER JOIN wroteRelation AS wr2
  ON citesRelation.eidCited = wr2.eid
WHERE authorScopus.id = '22950236500'
ORDER BY authorCited