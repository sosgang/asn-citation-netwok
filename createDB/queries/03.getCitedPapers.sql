SELECT curriculum.authorId, wroteRelation.eid  AS eidCiting, citesRelation.eidCited
FROM curriculum
INNER JOIN wroteRelation
  ON curriculum.authorId = wroteRelation.authorId
INNER JOIN citesRelation
  ON wroteRelation.eid = citesRelation.eidCiting
WHERE curriculum.authorId = '8984218100'
