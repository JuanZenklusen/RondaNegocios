from django.db import models


class Match(models.Model):
    """Compatibilidad calculada entre dos empresas de una misma organización.

    Se guarda un único registro por par no ordenado (company_a.id < company_b.id).
    `score` va de 0 a 100. `details` guarda el desglose del cálculo.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="matches",
        verbose_name="organización",
    )
    company_a = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="matches_as_a",
        verbose_name="empresa A",
    )
    company_b = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="matches_as_b",
        verbose_name="empresa B",
    )
    score = models.PositiveSmallIntegerField("compatibilidad (%)", default=0)
    details = models.JSONField("desglose", default=dict, blank=True)
    updated_at = models.DateTimeField("actualizado", auto_now=True)

    class Meta:
        verbose_name = "match"
        verbose_name_plural = "matches"
        ordering = ["-score"]
        constraints = [
            models.UniqueConstraint(fields=["company_a", "company_b"], name="unique_match_pair"),
        ]

    def __str__(self):
        return f"{self.company_a} ⇄ {self.company_b}: {self.score}%"
