from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PagoCuota, Cuota, Pago

@receiver(post_save, sender=PagoCuota)
def actualizar_cuota_al_pagar(sender, instance, created, **kwargs):
    """
    Cuando se crea o actualiza un PagoCuota, actualiza el estado de la cuota
    """
    cuota = instance.cuota
    
    # Si el pago está verificado, marcar la cuota como pagada
    if instance.pago.estado == 'VERIFICADO':
        # Verificar si el monto aplicado cubre el total
        if instance.monto_aplicado >= cuota.total_a_pagar():
            cuota.pagada = True
            cuota.recargo = 0
        else:
            # Pago parcial, reducir el monto pendiente
            cuota.monto = cuota.monto - instance.monto_aplicado
            cuota.pagada = False
        
        cuota.save()

@receiver(post_delete, sender=PagoCuota)
def revertir_pago_al_eliminar(sender, instance, **kwargs):
    """
    Cuando se elimina un PagoCuota, revierte el estado de la cuota si es necesario
    """
    cuota = instance.cuota
    
    # Si la cuota estaba marcada como pagada y el pago estaba verificado
    if cuota.pagada and instance.pago.estado == 'VERIFICADO':
        # Restaurar el estado de la cuota
        cuota.pagada = False
        cuota.actualizar_recargo()  # Recalcular recargos
        cuota.save()

@receiver(post_save, sender=Pago)
def actualizar_cuotas_al_verificar_pago(sender, instance, **kwargs):
    """
    Cuando un pago cambia de estado a VERIFICADO, actualiza todas las cuotas relacionadas
    """
    # Solo procesar si el pago está verificado
    if instance.estado == 'VERIFICADO':
        for pago_cuota in instance.pagocuota_set.all():
            cuota = pago_cuota.cuota
            
            # Verificar si el monto aplicado cubre el total
            if pago_cuota.monto_aplicado >= cuota.total_a_pagar():
                cuota.pagada = True
                cuota.recargo = 0
            else:
                # Pago parcial, reducir el monto pendiente
                cuota.monto = cuota.monto - pago_cuota.monto_aplicado
                cuota.pagada = False
            
            cuota.save()
    
    # Si el pago fue rechazado, revertir el estado de todas las cuotas
    if instance.estado == 'RECHAZADO':
        for pago_cuota in instance.pagocuota_set.all():
            cuota = pago_cuota.cuota
            if cuota.pagada:
                cuota.pagada = False
                cuota.actualizar_recargo()
                cuota.save()