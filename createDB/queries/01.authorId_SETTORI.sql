SELECT authorId
FROM cercauniversita
WHERE 
  authorId <> '' AND
  settore = '01/B1' 
UNION
select authorId
FROM curriculum
WHERE 
  authorId NOT LIKE 'MISSING%' AND
  settore = '01/B1'
 ORDER BY authorId
