SELECT authorId
FROM cercauniversita
WHERE authorId <> ''
UNION
select authorId
FROM curriculum
WHERE authorId NOT LIKE 'MISSING%'
