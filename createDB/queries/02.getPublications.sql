SELECT curriculum.authorId, wroteRelation.eid
FROM curriculum
INNER JOIN wroteRelation
  ON curriculum.authorId = wroteRelation.authorId
WHERE curriculum.authorId = '8984218100'
