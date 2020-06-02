from django.db import models


class SD(models.Model):
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    layer = models.CharField(max_length=2, blank=True, null=True, default=None)
    parent = models.ForeignKey("self", blank=True, null=True, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.value} - {self.layer}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            obj = SD.objects.filter(name=self.name, value=self.value, layer=self.layer, parent=self.parent)
            if not obj:
                print(f"Create {self.name}, {self.value}, {self.layer}, {self.parent}")
                super(SD, self).save(*args, **kwargs)
            else:
                print(f"Exist {self.name}, {self.value}, {self.layer}, {self.parent}")
        else:
            super(SD, self).save(*args, **kwargs)
